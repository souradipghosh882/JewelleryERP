import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/api_client.dart';
import '../../../core/theme.dart';

class AddOrnamentScreen extends ConsumerStatefulWidget {
  const AddOrnamentScreen({super.key});

  @override
  ConsumerState<AddOrnamentScreen> createState() => _AddOrnamentScreenState();
}

class _AddOrnamentScreenState extends ConsumerState<AddOrnamentScreen> {
  final _formKey = GlobalKey<FormState>();
  bool _loading = false;

  // Form fields
  String _name = '';
  String _metalType = 'gold_22k';
  String _category = 'RNG';
  double _grossWeight = 0;
  double _netWeight = 0;
  double _stoneWeight = 0;
  double _stoneRate = 0;
  String _makingChargeType = 'percent';
  double _makingChargeValue = 0;
  double _hallmarkCharge = 45;
  double _otherCharges = 0;
  String _description = '';

  final _metalTypes = {
    'gold_22k': '22K Gold',
    'gold_18k': '18K Gold',
    'gold_24k': '24K Gold',
    'gold_14k': '14K Gold',
    'silver': 'Silver',
    'silver_925': 'Sterling Silver 925',
  };

  final _categories = {
    'RNG': 'Ring',
    'NCK': 'Necklace',
    'EAR': 'Earring',
    'BNG': 'Bangle',
    'BRC': 'Bracelet',
    'CHN': 'Chain',
    'PND': 'Pendant',
    'ANK': 'Anklet',
    'MGS': 'Mangalsutra',
    'NSR': 'Nose Ring',
    'UTN': 'Utensil',
    'OTH': 'Other',
  };

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();
    setState(() => _loading = true);

    try {
      final dio = ref.read(dioProvider);
      await dio.post('/inventory/ornaments', data: {
        'name': _name,
        'metal_type': _metalType,
        'category': _category,
        'gross_weight': _grossWeight,
        'net_weight': _netWeight,
        'stone_weight': _stoneWeight,
        'stone_rate': _stoneRate,
        'making_charge_type': _makingChargeType,
        'making_charge_value': _makingChargeValue,
        'hallmark_charge': _hallmarkCharge,
        'other_charges': _otherCharges,
        'description': _description,
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Ornament added & tag generated!'),
              backgroundColor: AppTheme.successGreen),
        );
        context.go('/inventory');
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
      appBar: AppBar(title: const Text('Add Ornament')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildSection('Basic Info', [
              TextFormField(
                decoration: const InputDecoration(labelText: 'Ornament Name *'),
                validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                onSaved: (v) => _name = v!,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: _metalType,
                decoration: const InputDecoration(labelText: 'Metal Type *'),
                items: _metalTypes.entries
                    .map((e) => DropdownMenuItem(value: e.key, child: Text(e.value)))
                    .toList(),
                onChanged: (v) => setState(() => _metalType = v!),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: _category,
                decoration: const InputDecoration(labelText: 'Category *'),
                items: _categories.entries
                    .map((e) => DropdownMenuItem(value: e.key, child: Text(e.value)))
                    .toList(),
                onChanged: (v) => setState(() => _category = v!),
              ),
            ]),
            _buildSection('Weight (grams)', [
              Row(
                children: [
                  Expanded(child: _weightField('Gross Weight *', (v) => _grossWeight = v)),
                  const SizedBox(width: 12),
                  Expanded(child: _weightField('Net Weight *', (v) => _netWeight = v)),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(child: _weightField('Stone Weight', (v) => _stoneWeight = v, required: false)),
                  const SizedBox(width: 12),
                  Expanded(child: _weightField('Stone Rate (₹/g)', (v) => _stoneRate = v, required: false)),
                ],
              ),
            ]),
            _buildSection('Making Charges', [
              DropdownButtonFormField<String>(
                value: _makingChargeType,
                decoration: const InputDecoration(labelText: 'Charge Type'),
                items: const [
                  DropdownMenuItem(value: 'percent', child: Text('Percentage (%)')),
                  DropdownMenuItem(value: 'per_gram', child: Text('Per Gram (₹/g)')),
                ],
                onChanged: (v) => setState(() => _makingChargeType = v!),
              ),
              const SizedBox(height: 12),
              TextFormField(
                decoration: InputDecoration(
                  labelText: _makingChargeType == 'percent' ? 'Making % *' : 'Rate per gram (₹) *',
                ),
                keyboardType: TextInputType.number,
                validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                onSaved: (v) => _makingChargeValue = double.parse(v!),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(child: _weightField('Hallmark (₹)', (v) => _hallmarkCharge = v, required: false, initial: '45')),
                  const SizedBox(width: 12),
                  Expanded(child: _weightField('Other (₹)', (v) => _otherCharges = v, required: false)),
                ],
              ),
            ]),
            _buildSection('Notes', [
              TextFormField(
                decoration: const InputDecoration(labelText: 'Description / Notes'),
                maxLines: 3,
                onSaved: (v) => _description = v ?? '',
              ),
            ]),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _loading ? null : _submit,
              child: _loading
                  ? const CircularProgressIndicator()
                  : const Text('Add Ornament & Generate Tag'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const Divider(),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _weightField(String label, Function(double) onSaved, {bool required = true, String? initial}) {
    return TextFormField(
      initialValue: initial,
      decoration: InputDecoration(labelText: label),
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
      validator: required ? (v) => v == null || v.isEmpty ? 'Required' : null : null,
      onSaved: (v) => onSaved(double.tryParse(v ?? '') ?? 0),
    );
  }
}
