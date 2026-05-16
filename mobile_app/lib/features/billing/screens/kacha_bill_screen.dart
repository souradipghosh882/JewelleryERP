import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class KachaBillScreen extends ConsumerStatefulWidget {
  const KachaBillScreen({super.key});

  @override
  ConsumerState<KachaBillScreen> createState() => _KachaBillScreenState();
}

class _KachaBillScreenState extends ConsumerState<KachaBillScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Kacha Bill')),
      body: const Center(child: Text('Kacha Bill — coming soon')),
    );
  }
}
