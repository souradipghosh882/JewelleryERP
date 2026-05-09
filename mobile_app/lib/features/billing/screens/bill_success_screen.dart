import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme.dart';

class BillSuccessScreen extends StatelessWidget {
  final Map<String, dynamic> billData;
  const BillSuccessScreen({super.key, required this.billData});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.check_circle, color: AppTheme.successGreen, size: 80),
              const SizedBox(height: 24),
              const Text('Bill Generated!',
                  style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text(
                billData['bill_number'] ?? '',
                style: const TextStyle(fontSize: 18, color: AppTheme.primaryGold, fontFamily: 'monospace'),
              ),
              const SizedBox(height: 8),
              Text(
                'Total: ₹${(billData['total_amount'] as num?)?.toStringAsFixed(2) ?? ''}',
                style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 40),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {/* TODO: download PDF */},
                      icon: const Icon(Icons.download),
                      label: const Text('Download PDF'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => context.go('/billing'),
                      icon: const Icon(Icons.add),
                      label: const Text('New Bill'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              TextButton(
                onPressed: () => context.go('/dashboard'),
                child: const Text('Go to Dashboard'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
