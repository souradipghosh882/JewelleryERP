import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme.dart';

class BillingScreen extends StatelessWidget {
  const BillingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Billing')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              'Select Bill Type',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'Pakka bills include GST and are legally required for card/UPI payments.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 40),
            _BillTypeCard(
              title: 'Pakka Bill',
              subtitle: 'With GST • Legal • Card/UPI/Cash',
              icon: Icons.receipt,
              color: Colors.green,
              onTap: () => context.go('/billing/pakka'),
            ),
            const SizedBox(height: 20),
            _BillTypeCard(
              title: 'Kacha Bill',
              subtitle: 'No GST • Cash Only • Internal',
              icon: Icons.receipt_long,
              color: Colors.blue,
              onTap: () => context.go('/billing/kacha'),
            ),
          ],
        ),
      ),
    );
  }
}

class _BillTypeCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  const _BillTypeCard({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          border: Border.all(color: color, width: 2),
          borderRadius: BorderRadius.circular(16),
          color: color.withOpacity(0.05),
        ),
        child: Row(
          children: [
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 32),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      style: TextStyle(
                          fontSize: 20, fontWeight: FontWeight.bold, color: color)),
                  Text(subtitle, style: const TextStyle(color: Colors.grey)),
                ],
              ),
            ),
            Icon(Icons.arrow_forward_ios, color: color),
          ],
        ),
      ),
    );
  }
}
