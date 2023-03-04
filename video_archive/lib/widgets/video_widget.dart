import 'dart:io';

import 'package:flutter/material.dart';

class Video extends StatelessWidget {
  final String path;
  final String thumbnail;
  const Video({super.key, required this.path, required this.thumbnail});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: [
          Expanded(
            child: Container(
              // child: thumbnail,
              child: Image.file(File(thumbnail)),
            ),
          ),
          const Text("{Title of the Video}"),
          Text(path),
        ],
      ),
    );
  }
}
