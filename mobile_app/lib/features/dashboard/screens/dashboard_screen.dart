import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api_client.dart';
import '../../../core/theme.dart';
import '../../auth/providers/auth_provider.dart';

final dashboardProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, period) async {
  final dio = ref.read(dioProvider);
  final response = await dio.get('/analytics/dashboard', queryParameters: {'period': period});
  return response.data as Map<String, dynamic>;
});

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  String _period = 'today';

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authStateProvider);
    final dashboardAsync = ref.watch(dashboardProvider(_period));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(dashboardProvider(_period)),
          ),
        ],
      ),
      body: Column(
        children: [
          // Period Selector
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
            child: dashboardAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('Error: $e')),
              data: (data) => _buildDashboard(data, auth.role ?? ''),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDashboard(Map<String, dynamic> data, String role) {
    final pakka = data['pakka'] as Map<String, dynamic>;
    final kacha = data['kacha'] as Map<String, dynamic>;
    final inventory = data['inventory'] as Map<String, dynamic>? ?? {};

    return RefreshIndicator(
      onRefresh: () async => ref.invalidate(dashboardProvider(_period)),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _MetricCard(
            title: 'Total Revenue',
            value: '₹${_fmt(data['combined_revenue'])}',
            icon: Icons.currency_rupee,
            color: AppTheme.primaryGold,
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _MetricCard(
                  title: 'Pakka Sales',
                  value: '₹${_fmt(pakka['total_amount'])}',
                  subtitle: '${pakka['sales_count']} bills',
                  icon: Icons.receipt,
                  color: Colors.green,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _MetricCard(
                  title: 'Kacha Sales',
                  value: '₹${_fmt(kacha['total_amount'])}',
                  subtitle: '${kacha['sales_count']} bills',
                  icon: Icons.receipt_long,
                  color: Colors.blue,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (role == 'owner' || role == 'accountant')
            _MetricCard(
              title: 'GST Collected',
              value: '₹${_fmt(pakka['gst_collected'])}',
              icon: Icons.account_balance,
              color: Colors.orange,
            ),
          const SizedBox(height: 12),
          _MetricCard(
            title: 'Gold Stock',
            value: '${(data['gold_stock_grams'] as num).toStringAsFixed(2)} g',
            icon: Icons.diamond,
            color: AppTheme.accentGold,
          ),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Inventory Status',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 12),
                  ...inventory.entries.map((e) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(_statusLabel(e.key)),
                            Chip(label: Text('${e.value}')),
                          ],
                        ),
                      )),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _fmt(dynamic value) {
    final n = (value as num).toDouble();
    if (n >= 100000) return '${(n / 100000).toStringAsFixed(1)}L';
    if (n >= 1000) return '${(n / 1000).toStringAsFixed(1)}K';
    return n.toStringAsFixed(0);
  }

  String _statusLabel(String status) {
    const labels = {
      'in_stock': 'In Stock',
      'sold': 'Sold',
      'on_approval': 'On Approval',
      'returned': 'Returned',
    };
    return labels[status] ?? status;
  }
}

class _MetricCard extends StatelessWidget {
  final String title;
  final String value;
  final String? subtitle;
  final IconData icon;
  final Color color;

  const _MetricCard({
    required this.title,
    required this.value,
    this.subtitle,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 26),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
                  Text(value,
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 22)),
                  if (subtitle != null)
                    Text(subtitle!, style: TextStyle(color: Colors.grey.shade500, fontSize: 12)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
