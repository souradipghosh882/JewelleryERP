import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api_client.dart';

class SchemesScreen extends ConsumerWidget {
  const SchemesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Schemes')),
      body: FutureBuilder(
        future: ref.read(dioProvider).get('/schemes/'),
        builder: (context, snapshot) {
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
          final schemes = snapshot.data!.data as List<dynamic>;
          return ListView.builder(
            itemCount: schemes.length,
            itemBuilder: (_, i) {
              final s = schemes[i] as Map<String, dynamic>;
              return Card(
                margin: const EdgeInsets.all(8),
                child: ListTile(
                  leading: const Icon(Icons.savings, color: Colors.amber),
                  title: Text(s['name'] as String),
                  subtitle: Text('${s['duration_months']} months · ${s['scheme_type']}'),
                  trailing: s['bonus_month'] == true
                      ? const Chip(label: Text('Bonus Month'))
                      : null,
                ),
              );
            },
          );
        },
      ),
    );
  }
}
