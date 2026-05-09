import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme.dart';
import '../../auth/providers/auth_provider.dart';

class ShellScreen extends ConsumerWidget {
  final Widget child;
  const ShellScreen({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authStateProvider);
    final location = GoRouterState.of(context).matchedLocation;

    // Role-based navigation items
    final navItems = _getNavItems(auth.role ?? '');

    int selectedIndex = navItems.indexWhere((item) =>
        location.startsWith(item.route));
    if (selectedIndex == -1) selectedIndex = 0;

    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: selectedIndex.clamp(0, navItems.length - 1),
        onDestinationSelected: (i) => context.go(navItems[i].route),
        destinations: navItems
            .map((item) => NavigationDestination(
                  icon: Icon(item.icon),
                  label: item.label,
                ))
            .toList(),
      ),
    );
  }

  List<_NavItem> _getNavItems(String role) {
    final all = [
      _NavItem(Icons.dashboard, 'Dashboard', '/dashboard'),
      _NavItem(Icons.inventory_2, 'Inventory', '/inventory'),
      _NavItem(Icons.receipt_long, 'Billing', '/billing'),
      _NavItem(Icons.qr_code_scanner, 'Scanner', '/scanner'),
      _NavItem(Icons.people, 'Customers', '/customers'),
      _NavItem(Icons.savings, 'Schemes', '/schemes'),
      _NavItem(Icons.analytics, 'Analytics', '/analytics'),
      _NavItem(Icons.monetization_on, 'Rates', '/rates'),
      _NavItem(Icons.account_balance_wallet, 'Rokar', '/rokar'),
    ];

    switch (role) {
      case 'salesman':
        return all.where((i) => ['/dashboard', '/inventory', '/billing', '/scanner', '/customers'].contains(i.route)).toList();
      case 'tagger':
        return all.where((i) => ['/dashboard', '/inventory', '/scanner'].contains(i.route)).toList();
      case 'accountant':
        return all.where((i) => ['/dashboard', '/analytics', '/rokar', '/schemes'].contains(i.route)).toList();
      default: // owner, manager
        return all;
    }
  }
}

class _NavItem {
  final IconData icon;
  final String label;
  final String route;
  const _NavItem(this.icon, this.label, this.route);
}
