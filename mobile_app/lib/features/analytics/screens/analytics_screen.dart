import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/api_client.dart';
import '../../../core/theme.dart';

class AnalyticsScreen extends ConsumerStatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  ConsumerState<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends ConsumerState<AnalyticsScreen> {
  String _period = 'month';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Analytics')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'today', label: Text('Today')),
                ButtonSegment(value: 'week', label: Text('Week')),
                ButtonSegment(value: 'month', label: Text('Month')),
                ButtonSegment(value: 'year', label: Text('Year')),
              ],
              selected: {_period},
              onSelectionChanged: (v) => setState(() => _period = v.first),
            ),
          ),
          Expanded(
            child: FutureBuilder(
              future: ref.read(dioProvider).get('/analytics/dashboard', queryParameters: {'period': _period}),
              builder: (context, snapshot) {
                if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
                final data = snapshot.data!.data as Map<String, dynamic>;
                final pakka = data['pakka'] as Map<String, dynamic>;
                final kacha = data['kacha'] as Map<String, dynamic>;

                return ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    // Pie Chart
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          children: [
                            const Text('Revenue Split', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                            const SizedBox(height: 16),
                            SizedBox(
                              height: 200,
                              child: PieChart(PieChartData(
                                sections: [
                                  PieChartSectionData(
                                    value: (pakka['total_amount'] as num).toDouble(),
                                    title: 'Pakka',
                                    color: Colors.green,
                                  ),
                                  PieChartSectionData(
                                    value: (kacha['total_amount'] as num).toDouble(),
                                    title: 'Kacha',
                                    color: Colors.blue,
                                  ),
                                ],
                              )),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    _StatCard('Pakka Revenue', '₹${(pakka['total_amount'] as num).toStringAsFixed(0)}', '${pakka['sales_count']} bills', Colors.green),
                    const SizedBox(height: 8),
                    _StatCard('Kacha Revenue', '₹${(kacha['total_amount'] as num).toStringAsFixed(0)}', '${kacha['sales_count']} bills', Colors.blue),
                    const SizedBox(height: 8),
                    _StatCard('GST Collected', '₹${(pakka['gst_collected'] as num).toStringAsFixed(0)}', 'From pakka bills', Colors.orange),
                    const SizedBox(height: 8),
                    _StatCard('Gold Stock', '${(data['gold_stock_grams'] as num).toStringAsFixed(2)}g', 'In inventory', AppTheme.primaryGold),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title, value, subtitle;
  final Color color;
  const _StatCard(this.title, this.value, this.subtitle, this.color);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Container(
          width: 4,
          height: 48,
          decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(2)),
        ),
        title: Text(title, style: const TextStyle(fontSize: 13, color: Colors.grey)),
        subtitle: Text(subtitle, style: const TextStyle(fontSize: 12)),
        trailing: Text(value, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: color)),
      ),
    );
  }
}
