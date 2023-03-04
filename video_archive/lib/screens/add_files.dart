import 'dart:convert';
import 'dart:io';

import 'package:dotted_border/dotted_border.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:video_archive/models/get_files.dart';

late String? result;

class AddFiles extends StatelessWidget {
  late String url;
  var Data;
  Map<String, dynamic> thumbnails = {};
  // AddFiles({super.key});

  final AppBar _appBar = AppBar(
    title: const Text("Video Archive App"),
    centerTitle: true,
  );


  void _pickFile(BuildContext context) async {
    // FilePickerResult? result = await FilePicker.platform.pickFiles(
    //   allowMultiple: true,
    //   dialogTitle: "Select video files for upload",
    //   type: FileType.video,
    // );
    thumbnails.clear();
    result = await FilePicker.platform.getDirectoryPath();

    if (result == null) return;
    url = "http://127.0.0.1:5000/setup?path=$result";
    Data = await GetData(url);
    var decoded = json.decode(Data);
    if (decoded['status'] == true) {
      //Create toast
      print(result);
      print("Encoding complete");
      thumbnails = decoded['thumbnails'];
      //move to show screen with navigator
      Navigator.of(context).pushNamed("/show_files", arguments: thumbnails);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: _appBar,
      body: Container(
        margin: const EdgeInsets.all(10),
        alignment: Alignment.center,
        child: DottedBorder(
          color: Theme.of(context).primaryColor,
          dashPattern: const [50, 20],
          strokeWidth: 10,
          strokeCap: StrokeCap.round,
          // borderPadding: EdgeInsets.all(10),
          child: Container(
            margin: const EdgeInsets.all(2),
            child: IconButton(
              onPressed: () => _pickFile(context),
              icon: Column(
                children: const [
                  Icon(
                    Icons.add_box_outlined,
                    size: 80,
                  ),
                  Text("Add files for upload"),
                ],
              ),
              padding: EdgeInsets.symmetric(
                vertical: MediaQuery.of(context).size.height / 2 - 120,
                horizontal: MediaQuery.of(context).size.width / 2 - 100,
              ),
              highlightColor: Colors.green,
              hoverColor: Colors.grey[300],
              style: ButtonStyle(
                shape: MaterialStateProperty.all<ContinuousRectangleBorder>(
                  const ContinuousRectangleBorder(
                    borderRadius: BorderRadius.all(Radius.circular(10)),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
