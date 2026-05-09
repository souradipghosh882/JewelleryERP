import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api_client.dart';

final customersListProvider = FutureProvider<List<dynamic>>((ref) async {
  final dio = ref.read(dioProvider);
  final response = await dio.get('/customers/', queryParameters: {'limit': 100});
  return response.data as List<dynamic>;
});

class CustomersScreen extends ConsumerWidget {
  const CustomersScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final customersAsync = ref.watch(customersListProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Customers')),
      floatingActionButton: FloatingActionButton(
        onPressed: () {/* TODO: add customer */},
        child: const Icon(Icons.add),
      ),
      body: customersAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (customers) => ListView.builder(
          itemCount: customers.length,
          itemBuilder: (_, i) {
            final c = customers[i] as Map<String, dynamic>;
            return ListTile(
              leading: CircleAvatar(child: Text((c['name'] as String)[0])),
              title: Text(c['name'] as String),
              subtitle: Text(c['phone'] as String),
              trailing: c['kyc_status'] != 'none'
                  ? const Icon(Icons.verified, color: Colors.green)
                  : null,
            );
          },
        ),
      ),
    );
  }
}
