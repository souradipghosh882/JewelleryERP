import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'features/auth/screens/login_screen.dart';
import 'features/dashboard/screens/dashboard_screen.dart';
import 'features/inventory/screens/inventory_list_screen.dart';
import 'features/inventory/screens/ornament_detail_screen.dart';
import 'features/inventory/screens/add_ornament_screen.dart';
import 'features/billing/screens/billing_screen.dart';
import 'features/billing/screens/pakka_bill_screen.dart';
import 'features/billing/screens/kacha_bill_screen.dart';
import 'features/billing/screens/bill_success_screen.dart';
import 'features/scanner/screens/scanner_screen.dart';
import 'features/customers/screens/customers_screen.dart';
import 'features/customers/screens/customer_detail_screen.dart';
import 'features/schemes/screens/schemes_screen.dart';
import 'features/analytics/screens/analytics_screen.dart';
import 'features/rates/screens/metal_rates_screen.dart';
import 'features/rokar/screens/rokar_screen.dart';
import 'features/auth/providers/auth_provider.dart';
import 'shared/screens/shell_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) {
      final isLoggedIn = authState.isAuthenticated;
      final isLoginPage = state.matchedLocation == '/login';

      if (!isLoggedIn && !isLoginPage) return '/login';
      if (isLoggedIn && isLoginPage) return '/dashboard';
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      ShellRoute(
        builder: (context, state, child) => ShellScreen(child: child),
        routes: [
          GoRoute(
            path: '/dashboard',
            builder: (context, state) => const DashboardScreen(),
          ),
          GoRoute(
            path: '/inventory',
            builder: (context, state) => const InventoryListScreen(),
            routes: [
              GoRoute(
                path: 'add',
                builder: (context, state) => const AddOrnamentScreen(),
              ),
              GoRoute(
                path: ':id',
                builder: (context, state) =>
                    OrnamentDetailScreen(ornamentId: state.pathParameters['id']!),
              ),
            ],
          ),
          GoRoute(
            path: '/billing',
            builder: (context, state) => const BillingScreen(),
            routes: [
              GoRoute(
                path: 'pakka',
                builder: (context, state) => const PakkaBillScreen(),
              ),
              GoRoute(
                path: 'kacha',
                builder: (context, state) => const KachaBillScreen(),
              ),
              GoRoute(
                path: 'success',
                builder: (context, state) => BillSuccessScreen(
                  billData: state.extra as Map<String, dynamic>,
                ),
              ),
            ],
          ),
          GoRoute(
            path: '/scanner',
            builder: (context, state) => const ScannerScreen(),
          ),
          GoRoute(
            path: '/customers',
            builder: (context, state) => const CustomersScreen(),
            routes: [
              GoRoute(
                path: ':id',
                builder: (context, state) =>
                    CustomerDetailScreen(customerId: state.pathParameters['id']!),
              ),
            ],
          ),
          GoRoute(
            path: '/schemes',
            builder: (context, state) => const SchemesScreen(),
          ),
          GoRoute(
            path: '/analytics',
            builder: (context, state) => const AnalyticsScreen(),
          ),
          GoRoute(
            path: '/rates',
            builder: (context, state) => const MetalRatesScreen(),
          ),
          GoRoute(
            path: '/rokar',
            builder: (context, state) => const RokarScreen(),
          ),
        ],
      ),
    ],
  );
});
