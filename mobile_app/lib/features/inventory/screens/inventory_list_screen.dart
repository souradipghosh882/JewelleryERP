import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/api_client.dart';
import '../../../core/theme.dart';

final inventoryProvider = FutureProvider.family<List<dynamic>, Map<String, String?>>((ref, filters) async {
  final dio = ref.read(dioProvider);
  final response = await dio.get('/inventory/ornaments', queryParameters: {
    if (filters['search'] != null) 'search': filters['search'],
    if (filters['status'] != null) 'status': filters['status'],
    if (filters['metal_type'] != null) 'metal_type': filters['metal_type'],
    'limit': '100',
  });
  return response.data as List<dynamic>;
});

class InventoryListScreen extends ConsumerStatefulWidget {
  const InventoryListScreen({super.key});

  @override
  ConsumerState<InventoryListScreen> createState() => _InventoryListScreenState();
}

class _InventoryListScreenState extends ConsumerState<InventoryListScreen> {
  String? _statusFilter;
  String? _metalFilter;
  String? _searchQuery;
  final _searchController = TextEditingController();

  Map<String, String?> get _filters => {
    'search': _searchQuery,
    'status': _statusFilter,
    'metal_type': _metalFilter,
  };

  @override
  Widget build(BuildContext context) {
    final inventoryAsync = ref.watch(inventoryProvider(_filters));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Inventory'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => context.go('/inventory/add'),
          ),
        ],
      ),
      body: Column(
        children: [
          // Search bar
          Padding(
            padding: const EdgeInsets.all(12),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search by name or tag code...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchQuery != null
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          setState(() => _searchQuery = null);
                        },
                      )
                    : null,
              ),
              onSubmitted: (v) => setState(() => _searchQuery = v.isEmpty ? null : v),
            ),
          ),
          // Filter chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Row(
              children: [
                _FilterChip('All', null == _statusFilter, () => setState(() => _statusFilter = null)),
                const SizedBox(width: 8),
                _FilterChip('In Stock', 'in_stock' == _statusFilter, () => setState(() => _statusFilter = 'in_stock')),
                const SizedBox(width: 8),
                _FilterChip('Sold', 'sold' == _statusFilter, () => setState(() => _statusFilter = 'sold')),
                const SizedBox(width: 8),
                _FilterChip('Gold 22K', 'gold_22k' == _metalFilter, () => setState(() => _metalFilter = _metalFilter == 'gold_22k' ? null : 'gold_22k')),
                const SizedBox(width: 8),
                _FilterChip('Silver', 'silver' == _metalFilter, () => setState(() => _metalFilter = _metalFilter == 'silver' ? null : 'silver')),
              ],
            ),
          ),
          const SizedBox(height: 8),
          // List
          Expanded(
            child: inventoryAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('Error: $e')),
              data: (items) => items.isEmpty
                  ? const Center(child: Text('No ornaments found'))
                  : ListView.builder(
                      padding: const EdgeInsets.all(12),
                      itemCount: items.length,
                      itemBuilder: (context, i) => _OrnamentCard(item: items[i]),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;
  const _FilterChip(this.label, this.selected, this.onTap);

  @override
  Widget build(BuildContext context) {
    return FilterChip(
      label: Text(label),
      selected: selected,
      onSelected: (_) => onTap(),
      selectedColor: AppTheme.primaryGold.withOpacity(0.3),
    );
  }
}

class _OrnamentCard extends StatelessWidget {
  final Map<String, dynamic> item;
  const _OrnamentCard({required this.item});

  @override
  Widget build(BuildContext context) {
    final status = item['status'] as String;
    final statusColor = status == 'in_stock' ? Colors.green : status == 'sold' ? Colors.red : Colors.orange;

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: item['photo_path'] != null
            ? ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.network(
                  'http://localhost:8000/${item['photo_path']}',
                  width: 50,
                  height: 50,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => _goldIcon(),
                ),
              )
            : _goldIcon(),
        title: Text(
          item['name'] as String,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(item['tag_code'] as String,
                style: const TextStyle(fontSize: 12, fontFamily: 'monospace')),
            Text('${item['net_weight']}g · ${_metalLabel(item['metal_type'] as String)}'),
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: statusColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: statusColor),
          ),
          child: Text(
            status == 'in_stock' ? 'In Stock' : status.replaceAll('_', ' ').toUpperCase(),
            style: TextStyle(color: statusColor, fontSize: 11, fontWeight: FontWeight.w600),
          ),
        ),
        onTap: () => context.go('/inventory/${item['id']}'),
      ),
    );
  }

  Widget _goldIcon() => Container(
        width: 50,
        height: 50,
        decoration: BoxDecoration(
          color: AppTheme.primaryGold.withOpacity(0.2),
          borderRadius: BorderRadius.circular(8),
        ),
        child: const Icon(Icons.diamond, color: AppTheme.primaryGold),
      );

  String _metalLabel(String metal) {
    const labels = {
      'gold_22k': '22K Gold',
      'gold_18k': '18K Gold',
      'gold_24k': '24K Gold',
      'gold_14k': '14K Gold',
      'silver': 'Silver',
      'silver_925': '925 Silver',
    };
    return labels[metal] ?? metal;
  }
}
