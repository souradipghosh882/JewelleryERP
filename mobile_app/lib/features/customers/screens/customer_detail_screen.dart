import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api_client.dart';

class CustomerDetailScreen extends ConsumerWidget {
  final String customerId;
  const CustomerDetailScreen({super.key, required this.customerId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Customer Details')),
      body: FutureBuilder(
        future: ref.read(dioProvider).get('/customers/$customerId'),
        builder: (context, snapshot) {
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
          final c = snapshot.data!.data as Map<String, dynamic>;
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              ListTile(title: Text(c['name'] as String), subtitle: Text(c['phone'] as String)),
              if (c['email'] != null) ListTile(leading: const Icon(Icons.email), title: Text(c['email'] as String)),
              ListTile(leading: const Icon(Icons.verified_user), title: Text('KYC: ${c['kyc_status']}')),
            ],
          );
        },
      ),
    );
  }
}
