import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api_client.dart';
import '../../../core/theme.dart';
import 'package:qr_flutter/qr_flutter.dart';

final ornamentDetailProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, id) async {
  final dio = ref.read(dioProvider);
  final response = await dio.get('/inventory/ornaments/$id');
  return response.data as Map<String, dynamic>;
});

final currentRatesProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final dio = ref.read(dioProvider);
  final response = await dio.get('/rates/current');
  return response.data as Map<String, dynamic>;
});

class OrnamentDetailScreen extends ConsumerWidget {
  final String ornamentId;
  const OrnamentDetailScreen({super.key, required this.ornamentId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ornamentAsync = ref.watch(ornamentDetailProvider(ornamentId));
    final ratesAsync = ref.watch(currentRatesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Ornament Details')),
      body: ornamentAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (ornament) => _buildDetail(context, ornament, ratesAsync),
      ),
    );
  }

  Widget _buildDetail(BuildContext context, Map<String, dynamic> o, AsyncValue<Map<String, dynamic>> ratesAsync) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Tag Code + QR
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Text(
                  o['tag_code'] as String,
                  style: const TextStyle(
                    fontSize: 22, fontWeight: FontWeight.bold,
                    fontFamily: 'monospace', color: AppTheme.primaryGold,
                  ),
                ),
                const SizedBox(height: 12),
                QrImageView(
                  data: o['tag_code'] as String,
                  version: QrVersions.auto,
                  size: 160,
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        // Details
        _DetailCard('Item Info', [
          _row('Name', o['name'] as String),
          _row('Metal', _metalLabel(o['metal_type'] as String)),
          _row('Category', o['category'] as String),
          _row('Status', o['status'] as String),
          if (o['purity'] != null) _row('Purity', o['purity'] as String),
        ]),
        const SizedBox(height: 12),
        _DetailCard('Weights', [
          _row('Gross Weight', '${o['gross_weight']}g'),
          _row('Net Weight', '${o['net_weight']}g'),
          if ((o['stone_weight'] as num) > 0) _row('Stone Weight', '${o['stone_weight']}g'),
        ]),
        const SizedBox(height: 12),
        // Live Price Estimate
        ratesAsync.when(
          loading: () => const Card(child: Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator())),
          error: (_, __) => const Card(child: Padding(padding: EdgeInsets.all(16), child: Text('Rates unavailable'))),
          data: (rates) => _buildPriceEstimate(o, rates),
        ),
      ],
    );
  }

  Widget _buildPriceEstimate(Map<String, dynamic> o, Map<String, dynamic> rates) {
    final metalType = o['metal_type'] as String;
    final rateKey = metalType == 'gold_22k' ? 'gold_22k'
        : metalType == 'gold_18k' ? 'gold_18k'
        : metalType == 'gold_24k' ? 'gold_24k'
        : 'silver';
    final rate = (rates[rateKey] as num).toDouble();
    final netWeight = (o['net_weight'] as num).toDouble();
    final goldValue = netWeight * rate;

    double makingCharge = 0;
    if (o['making_charge_type'] == 'percent') {
      makingCharge = (o['making_charge_value'] as num) / 100 * rate * netWeight;
    } else {
      makingCharge = (o['making_charge_value'] as num) * netWeight;
    }

    final stoneValue = (o['stone_weight'] as num) * (o['stone_rate'] as num);
    final hallmark = (o['hallmark_charge'] as num).toDouble();
    final other = (o['other_charges'] as num).toDouble();
    final subtotal = goldValue + makingCharge + stoneValue + hallmark + other;
    final gst = subtotal * 0.03;
    final pakkaTotal = subtotal + gst;

    return _DetailCard('Live Price Estimate', [
      _row('Gold Rate', '₹${rate.toStringAsFixed(0)}/g'),
      _row('Gold Value', '₹${goldValue.toStringAsFixed(2)}'),
      _row('Making Charge', '₹${makingCharge.toStringAsFixed(2)}'),
      if (stoneValue > 0) _row('Stone Value', '₹${stoneValue.toStringAsFixed(2)}'),
      if (hallmark > 0) _row('Hallmark', '₹${hallmark.toStringAsFixed(2)}'),
      const Divider(),
      _row('Subtotal', '₹${subtotal.toStringAsFixed(2)}'),
      _row('GST (3%)', '₹${gst.toStringAsFixed(2)}'),
      _row('Pakka Total', '₹${pakkaTotal.toStringAsFixed(2)}', bold: true, color: AppTheme.primaryGold),
      _row('Kacha Total', '₹${subtotal.toStringAsFixed(2)}', bold: true, color: Colors.blue),
    ]);
  }

  Widget _DetailCard(String title, List<Widget> rows) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const Divider(),
            ...rows,
          ],
        ),
      ),
    );
  }

  Widget _row(String label, String value, {bool bold = false, Color? color}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey.shade600)),
          Text(
            value,
            style: TextStyle(
              fontWeight: bold ? FontWeight.bold : FontWeight.normal,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  String _metalLabel(String metal) {
    const labels = {
      'gold_22k': '22K Gold', 'gold_18k': '18K Gold',
      'gold_24k': '24K Gold', 'silver': 'Silver', 'silver_925': '925 Silver',
    };
    return labels[metal] ?? metal;
  }
}
