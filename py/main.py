import os
import glob
import torch
import hashlib
import open_clip
import argparse
import numpy as np
from clip_video_encode.reader import Reader
from clip_video_encode.writer import FileWriter
from torchvision.transforms import ToPILImage
from clip_video_encode.simplemapper import FrameMapper
from clip_video_encode.utils import block2dl
from video2numpy.frame_reader import FrameReader


def load_model():
    """Load the model and tokenizer."""
    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32", pretrained="laion2b_s34b_b79k", device="cpu")
    tokenizer = open_clip.get_tokenizer('ViT-B-32-quickgelu')
    preprocess.transforms = [ToPILImage()] + preprocess.transforms[-3:]
    return model, tokenizer, preprocess


def get_videos(folder):
    """Get all videos in a folder."""
    return sum(
        [[f"{folder}/{f}" for f in os.listdir(folder) if f.endswith(ext)] for ext in ['mp4', 'mkv', 'mov']], [])


def setup_embeds(folder, model, preprocess):
    """Sets up the embeddings for a folder of videos."""
    vidhash_path = os.path.join(folder, ".vidhash")
    if not os.path.exists(vidhash_path):
        hashfile = open(vidhash_path, 'w+').close()

    with open(vidhash_path, 'r+') as hashfile:
        hashes = [h.strip() for h in hashfile.readlines()]
        hashdict = {}
        unhashed = []
        videos = get_videos(folder)
        for vidpath in videos:
            videostream = open(vidpath, 'rb').read()
            h = hashlib.md5(videostream).hexdigest()
            if h not in hashes:
                unhashed.append(vidpath)
            hashdict[h] = vidpath

        hashfile.seek(0)
        hashfile.truncate()
        hashfile.write("\n".join(hashdict.keys()))

    if len(unhashed) == 0:
        print("No new videos found.")
    else:
        print(f"{len(unhashed)} new videos found.")
        reader = Reader(unhashed, [])
        vids, ids, meta = reader.get_data()

        meta_refs = list(range(len(vids)))
        vidembs_path = os.path.join(folder, ".vidembs")
        if not os.path.exists(vidembs_path):
            os.mkdir(vidembs_path)
        writer = FileWriter(vidembs_path)

        print("Loading videos...")
        fm = FrameMapper(model, "cpu")
        fr = FrameReader(vids, meta_refs, 5, 224, workers=1, memory_size=2)
        frames, ind_dict = [], {}
        block_size = 0
        i = 0
        fr.start_reading()
        for vid_frames, info in fr:
            i += 1
            frames.append(vid_frames)
            ind_dict[info["reference"]] = (block_size,
                                           block_size + vid_frames.shape[0],
                                           info["dst_name"])
            block_size += vid_frames.shape[0]
        print("Encoding videos...")
        vid_block = np.concatenate(frames)
        dl = block2dl(vid_block, preprocess, 16, 1)

        embeddings = []
        for batch in dl:
            with torch.no_grad():
                emb = fm(batch.to("cpu"))
                embeddings.append(emb)

        embeddings = np.concatenate(embeddings)
        for ref, (i0, it, dst_name) in ind_dict.items():
            vid_id = os.path.splitext(dst_name)[0]
            vid_meta = {}
            for k in meta:
                vid_meta[k] = meta[k][ref].as_py()
            writer.write(embeddings[i0:it], vid_id, vid_meta)


def search_videos(search, folder, model, tokenizer):
    print(folder)
    text = tokenizer([f"a photo of {search}", "a photo of something"])
    output_ls = []
    with torch.no_grad():
        text_emb = model.encode_text(text)
        text_emb /= text_emb.norm(dim=-1, keepdim=True)

        for vid in get_videos(folder):
            probls = []
            # extract the location of the npy file
            vid_name = os.path.splitext(os.path.basename(vid))[0]
            parent_dir = os.path.dirname(vid)
            npy_path = f"{os.path.join(parent_dir, '.vidembs', vid_name)}.npy"

            vid_emb = np.load(npy_path)
            vid_emb = torch.from_numpy(vid_emb)
            vid_emb /= vid_emb.norm(dim=-1, keepdim=True)

            # use the second text query as a baseline to apply softmax and get probs
            logit_scale = model.logit_scale.exp()
            logits_per_frame = logit_scale * vid_emb @ text_emb.t()
            text_prob = logits_per_frame.softmax(dim=-1).cpu().numpy()
            ps = text_prob[:, 0]

            conv_w = len(ps) // 5
            ps = np.convolve(ps, np.ones(conv_w) / conv_w, mode='same')
            if max(ps) > 0.8:
                output_ls.append((vid, ps.mean()))
    output_ls.sort(key=lambda x: x[1], reverse=True)
    return output_ls


def main(args):
    print("Loading model...")
    model, tokenizer, preprocess = load_model()

    print("Checking folder...")
    setup_embeds(args.folder, model, preprocess)
    output_ls = search_videos(args.search, args.folder, model, tokenizer)

    print("Videos likely to match the search query, in order:")
    for vid in output_ls:
        print(vid[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search through videos in a folder.")

    parser.add_argument(
        "search",
        type=str,
        help="Search query. Try to be as descriptive as possible",
    )
    parser.add_argument(
        "--folder",
        type=str,
        default="./",
        help=
        "Folder to search through. Note that subdirectories are not searched",
    )
    args = parser.parse_args()

    main(args)