import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:go_router/go_router.dart';
import '../../../core/api_client.dart';
import '../../../core/theme.dart';

class ScannerScreen extends ConsumerStatefulWidget {
  const ScannerScreen({super.key});

  @override
  ConsumerState<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends ConsumerState<ScannerScreen> {
  final MobileScannerController _controller = MobileScannerController();
  bool _scanned = false;
  bool _loading = false;
  Map<String, dynamic>? _scannedOrnament;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _onDetect(BarcodeCapture capture) async {
    if (_scanned || _loading) return;
    final barcode = capture.barcodes.firstOrNull;
    if (barcode?.rawValue == null) return;

    final tagCode = barcode!.rawValue!;
    setState(() {
      _scanned = true;
      _loading = true;
    });
    await _controller.stop();

    try {
      final dio = ref.read(dioProvider);
      final response = await dio.get('/inventory/scan/$tagCode');
      setState(() {
        _scannedOrnament = response.data as Map<String, dynamic>;
        _loading = false;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Tag not found: $tagCode'),
            backgroundColor: AppTheme.errorRed,
          ),
        );
        setState(() {
          _scanned = false;
          _loading = false;
        });
        await _controller.start();
      }
    }
  }

  void _reset() {
    setState(() {
      _scanned = false;
      _scannedOrnament = null;
    });
    _controller.start();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan Tag'),
        actions: [
          if (_scanned)
            TextButton(
              onPressed: _reset,
              child: const Text('Rescan', style: TextStyle(color: AppTheme.primaryGold)),
            ),
        ],
      ),
      body: _scannedOrnament != null
          ? _buildResult(_scannedOrnament!)
          : _buildScanner(),
    );
  }

  Widget _buildScanner() {
    return Column(
      children: [
        Expanded(
          flex: 3,
          child: Stack(
            children: [
              MobileScanner(controller: _controller, onDetect: _onDetect),
              Center(
                child: Container(
                  width: 250,
                  height: 250,
                  decoration: BoxDecoration(
                    border: Border.all(color: AppTheme.primaryGold, width: 3),
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
              ),
              if (_loading)
                Container(
                  color: Colors.black54,
                  child: const Center(
                    child: CircularProgressIndicator(color: AppTheme.primaryGold),
                  ),
                ),
            ],
          ),
        ),
        Expanded(
          flex: 1,
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.qr_code_scanner, size: 32, color: Colors.grey),
                const SizedBox(height: 8),
                const Text('Point camera at QR code or barcode on tag',
                    textAlign: TextAlign.center, style: TextStyle(color: Colors.grey)),
                const SizedBox(height: 12),
                IconButton(
                  icon: const Icon(Icons.flash_on),
                  onPressed: () => _controller.toggleTorch(),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildResult(Map<String, dynamic> o) {
    final status = o['status'] as String;
    final isInStock = status == 'in_stock';

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          color: isInStock ? Colors.green.shade50 : Colors.red.shade50,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Icon(
                  isInStock ? Icons.check_circle : Icons.cancel,
                  color: isInStock ? Colors.green : Colors.red,
                  size: 48,
                ),
                const SizedBox(height: 8),
                Text(
                  o['tag_code'] as String,
                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                Text(
                  isInStock ? 'Available for sale' : 'Not available (${status.replaceAll('_', ' ')})',
                  style: TextStyle(color: isInStock ? Colors.green : Colors.red),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(o['name'] as String, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                _infoRow('Metal', _metalLabel(o['metal_type'] as String)),
                _infoRow('Net Weight', '${o['net_weight']}g'),
                _infoRow('Category', o['category'] as String),
              ],
            ),
          ),
        ),
        if (isInStock) ...[
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => context.go('/billing/pakka'),
                  icon: const Icon(Icons.receipt),
                  label: const Text('Pakka Bill'),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => context.go('/billing/kacha'),
                  icon: const Icon(Icons.receipt_long),
                  label: const Text('Kacha Bill'),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.blue),
                ),
              ),
            ],
          ),
        ],
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () => context.go('/inventory/${o['id']}'),
          icon: const Icon(Icons.info_outline),
          label: const Text('View Full Details'),
        ),
      ],
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  String _metalLabel(String metal) {
    const labels = {'gold_22k': '22K Gold', 'gold_18k': '18K Gold', 'silver': 'Silver'};
    return labels[metal] ?? metal;
  }
}
