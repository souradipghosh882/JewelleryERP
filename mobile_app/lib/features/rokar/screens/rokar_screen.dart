import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api_client.dart';

class RokarScreen extends ConsumerWidget {
  const RokarScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Rokar (Cash Flow)')),
      floatingActionButton: FloatingActionButton(
        onPressed: () {/* TODO: add rokar entry */},
        child: const Icon(Icons.add),
      ),
      body: FutureBuilder(
        future: ref.read(dioProvider).get('/operations/rokar'),
        builder: (context, snapshot) {
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
          final data = snapshot.data!.data as Map<String, dynamic>;
          final entries = data['entries'] as List<dynamic>;
          return Column(
            children: [
              Container(
                margin: const EdgeInsets.all(16),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.green),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _CashStat('Cash In', '₹${(data['total_cash_in'] as num).toStringAsFixed(0)}', Colors.green),
                    _CashStat('Cash Out', '₹${(data['total_cash_out'] as num).toStringAsFixed(0)}', Colors.red),
                    _CashStat('Net', '₹${(data['net_cash'] as num).toStringAsFixed(0)}', Colors.blue),
                  ],
                ),
              ),
              Expanded(
                child: ListView.builder(
                  itemCount: entries.length,
                  itemBuilder: (_, i) {
                    final e = entries[i] as Map<String, dynamic>;
                    final isIn = e['entry_type'] == 'cash_in';
                    return ListTile(
                      leading: Icon(isIn ? Icons.arrow_downward : Icons.arrow_upward,
                          color: isIn ? Colors.green : Colors.red),
                      title: Text(e['description'] as String),
                      subtitle: Text(e['entry_date'] as String),
                      trailing: Text(
                        '${isIn ? '+' : '-'}₹${(e['amount'] as num).toStringAsFixed(0)}',
                        style: TextStyle(
                          color: isIn ? Colors.green : Colors.red,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _CashStat extends StatelessWidget {
  final String label, value;
  final Color color;
  const _CashStat(this.label, this.value, this.color);

  @override
  Widget build(BuildContext context) => Column(
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
          Text(value, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 16)),
        ],
      );
}
