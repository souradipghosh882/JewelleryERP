import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api_client.dart';
import '../../../core/theme.dart';

final ratesProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final dio = ref.read(dioProvider);
  final response = await dio.get('/rates/current');
  return response.data as Map<String, dynamic>;
});

class MetalRatesScreen extends ConsumerWidget {
  const MetalRatesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ratesAsync = ref.watch(ratesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Metal Rates'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(ratesProvider),
          ),
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _showUpdateRateDialog(context, ref),
          ),
        ],
      ),
      body: ratesAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (rates) => _buildRates(context, rates),
      ),
    );
  }

  Widget _buildRates(BuildContext context, Map<String, dynamic> rates) {
    final isStale = rates['is_stale'] as bool? ?? false;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (isStale)
          Container(
            margin: const EdgeInsets.only(bottom: 16),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.orange.shade50,
              border: Border.all(color: Colors.orange),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Row(
              children: [
                Icon(Icons.warning, color: Colors.orange),
                SizedBox(width: 8),
                Expanded(child: Text('Rates are stale! Please update today\'s rates.')),
              ],
            ),
          ),
        Text(
          'Session: ${rates['session']?.toString().toUpperCase() ?? ''} · ${rates['rate_date'] ?? ''}',
          style: const TextStyle(color: Colors.grey, fontSize: 13),
        ),
        const SizedBox(height: 16),
        const Text('Gold Rates (per gram)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        const SizedBox(height: 8),
        _RateCard('22K Gold', rates['gold_22k'], Colors.amber.shade700),
        _RateCard('24K Gold', rates['gold_24k'], Colors.amber.shade900),
        _RateCard('18K Gold', rates['gold_18k'], Colors.amber),
        if (rates['gold_14k'] != null) _RateCard('14K Gold', rates['gold_14k'], Colors.amber.shade300),
        if (rates['gold_9k'] != null) _RateCard('9K Gold', rates['gold_9k'], Colors.amber.shade200),
        const SizedBox(height: 16),
        const Text('Silver Rates (per gram)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        const SizedBox(height: 8),
        _RateCard('Silver', rates['silver'], Colors.grey.shade600),
        if (rates['silver_925'] != null) _RateCard('Sterling 925', rates['silver_925'], Colors.grey),
      ],
    );
  }

  void _showUpdateRateDialog(BuildContext context, WidgetRef ref) {
    // TODO: Show rate update form (owner only)
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Update Metal Rates'),
        content: const Text('Rate update form coming soon.'),
        actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))],
      ),
    );
  }
}

class _RateCard extends StatelessWidget {
  final String label;
  final dynamic rate;
  final Color color;
  const _RateCard(this.label, this.rate, this.color);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withOpacity(0.2),
          child: Text(label[0], style: TextStyle(color: color, fontWeight: FontWeight.bold)),
        ),
        title: Text(label),
        trailing: Text(
          '₹${(rate as num).toStringAsFixed(0)}/g',
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
      ),
    );
  }
}
