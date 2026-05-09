import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api_client.dart';
import '../../../core/theme.dart';

class PakkaBillScreen extends ConsumerStatefulWidget {
  const PakkaBillScreen({super.key});

  @override
  ConsumerState<PakkaBillScreen> createState() => _PakkaBillScreenState();
}

class _PakkaBillScreenState extends ConsumerState<PakkaBillScreen> {
  final List<Map<String, dynamic>> _cartItems = [];
  String? _customerId;
  String _paymentMode = 'cash';
  bool _loading = false;

  double get _subtotal => _cartItems.fold(0, (sum, i) => sum + (i['item_subtotal'] as double));
  double get _gst => _subtotal * 0.03;
  double get _total => _subtotal + _gst;

  Future<void> _createBill() async {
    if (_customerId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a customer'), backgroundColor: AppTheme.errorRed),
      );
      return;
    }
    if (_cartItems.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Cart is empty'), backgroundColor: AppTheme.errorRed),
      );
      return;
    }

    setState(() => _loading = true);
    try {
      final dio = ref.read(dioProvider);
      final response = await dio.post('/billing/pakka', data: {
        'customer_id': _customerId,
        'items': _cartItems.map((i) => {'ornament_id': i['id']}).toList(),
        'payment_mode': _paymentMode,
        'amount_paid': _total,
      });

      if (mounted) {
        // Navigate to success screen
        Navigator.of(context).pushReplacementNamed('/billing/success',
            arguments: response.data);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: AppTheme.errorRed),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pakka Bill'),
        backgroundColor: Colors.green.shade700,
      ),
      body: Column(
        children: [
          // Customer selector
          ListTile(
            leading: const Icon(Icons.person),
            title: Text(_customerId == null ? 'Select Customer *' : 'Customer selected'),
            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () {/* TODO: customer picker */},
          ),
          const Divider(),
          // Cart items
          Expanded(
            child: _cartItems.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.shopping_cart_outlined, size: 64, color: Colors.grey),
                        const SizedBox(height: 16),
                        const Text('No items. Scan tags to add.', style: TextStyle(color: Colors.grey)),
                        const SizedBox(height: 16),
                        ElevatedButton.icon(
                          onPressed: () {/* TODO: scan to add */},
                          icon: const Icon(Icons.qr_code_scanner),
                          label: const Text('Scan Item'),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    itemCount: _cartItems.length,
                    itemBuilder: (_, i) => ListTile(
                      title: Text(_cartItems[i]['name'] as String),
                      subtitle: Text(_cartItems[i]['tag_code'] as String),
                      trailing: Text('₹${(_cartItems[i]['item_subtotal'] as double).toStringAsFixed(0)}'),
                      leading: IconButton(
                        icon: const Icon(Icons.remove_circle, color: Colors.red),
                        onPressed: () => setState(() => _cartItems.removeAt(i)),
                      ),
                    ),
                  ),
          ),
          // Payment mode
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: DropdownButtonFormField<String>(
              value: _paymentMode,
              decoration: const InputDecoration(labelText: 'Payment Mode'),
              items: const [
                DropdownMenuItem(value: 'cash', child: Text('Cash')),
                DropdownMenuItem(value: 'card', child: Text('Card')),
                DropdownMenuItem(value: 'upi', child: Text('UPI')),
                DropdownMenuItem(value: 'bank_transfer', child: Text('Bank Transfer')),
              ],
              onChanged: (v) => setState(() => _paymentMode = v!),
            ),
          ),
          // Bill summary
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.green.shade50,
            child: Column(
              children: [
                _summaryRow('Subtotal', '₹${_subtotal.toStringAsFixed(2)}'),
                _summaryRow('GST (3%)', '₹${_gst.toStringAsFixed(2)}'),
                const Divider(),
                _summaryRow('Total', '₹${_total.toStringAsFixed(2)}', bold: true),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _createBill,
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                    child: _loading
                        ? const CircularProgressIndicator()
                        : const Text('Generate Pakka Bill', style: TextStyle(fontSize: 16)),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _summaryRow(String label, String value, {bool bold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: bold ? const TextStyle(fontWeight: FontWeight.bold) : null),
          Text(value, style: bold ? const TextStyle(fontWeight: FontWeight.bold, fontSize: 18) : null),
        ],
      ),
    );
  }
}
