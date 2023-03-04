// ignore_for_file: prefer_const_constructors

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:open_filex/open_filex.dart';

import '../models/get_files.dart';
import '../widgets/video_widget.dart';
import 'add_files.dart';

class ShowFiles extends StatefulWidget {
  String routeName = '/show_files';
  @override
  State<ShowFiles> createState() => _ShowFilesState();
}

class _ShowFilesState extends State<ShowFiles> {
  var _listData;

  Future<OpenResult> openFile(String filePath) async {
    // const filePath = '/storage/emulated/0/Download/flutter.png';
    return await OpenFilex.open(filePath);
  }

  late String url;
  Widget mainBody(TextEditingController textController, List<dynamic> paths,
      Map thumbnails) {
    if (textController.text.isEmpty) {
      return const Text(
        "Enter a query to search for",
        style: TextStyle(fontSize: 24),
      );
    } else if (paths.isEmpty) {
      return const Text(
        "No result found",
        style: TextStyle(fontSize: 24),
      );
    } else {
      return GridView.builder(
        gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
          maxCrossAxisExtent: 450,
          childAspectRatio: 1 / 1,
          crossAxisSpacing: 10,
          mainAxisSpacing: 10,
        ),
        itemBuilder: ((context, index) {
          return GestureDetector(
            child: Video(
              path: paths[index],
              thumbnail: thumbnails[paths[index]],
            ),
            onTap: () {
              openFile(paths[index]);
            },
          );
        }),
        itemCount: paths.length,
      );
    }
  }

  Widget body = const Text(
    "Enter a query to search for",
    style: TextStyle(fontSize: 24),
  );
  // const ShowFiles({super.key});
  final textController = TextEditingController();
  @override
  Widget build(BuildContext context) {
    final routeArgs =
        ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Video Archive App"),
        actions: [
          SizedBox(
            width: 200,
            child: TextField(
              keyboardType: TextInputType.name,
              maxLines: 1,
              decoration: const InputDecoration(
                label: Text("Query"),
              ),
              controller: textController,
              onChanged: (value) async {
                url = "http://127.0.0.1:5000/search?query=$value&path=$result";
                _listData = await GetData(url);
                var decoded = json.decode(_listData);
                List<dynamic> list = decoded['vid_paths'];

                // submitQuery(textController.text);
                setState(() {
                  body = mainBody(textController, list, routeArgs);
                });
              },
            ),
          ),
          IconButton(
            onPressed: () async {
              url = "http://127.0.0.1:5000/search?query=${textController.text}";
              _listData = await GetData(url);
              var decoded = json.decode(_listData) as Map<String, dynamic>;
              var list = decoded['vid_paths'];

              setState(() {
                body = mainBody(textController, list, routeArgs);
              });
            },
            icon: const Icon(Icons.search_outlined),
            tooltip: "Search",
          ),
        ],
        centerTitle: true,
      ),
      body: Container(
        margin: const EdgeInsets.all(10),
        alignment: Alignment.center,
        child: body,
      ),
    );
  }
}
