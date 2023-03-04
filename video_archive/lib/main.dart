// ignore_for_file: prefer_const_constructors, duplicate_ignore

import "package:flutter/material.dart";
import 'package:video_archive/models/material_color_generator.dart';
import 'package:video_archive/screens/add_files.dart';
import 'package:video_archive/screens/show_files.dart';


void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      // initialRoute: ,
      home: AddFiles(),
      routes: {
        '/show_files': (context) => ShowFiles(),
      },
      theme: ThemeData(
        useMaterial3: true,
        primarySwatch: generateMaterialColor(Color.fromRGBO(0, 162, 126, 1))
      ),
    );
  }
}

