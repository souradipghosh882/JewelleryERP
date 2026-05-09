import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../../core/api_client.dart';

// ─── Auth Models ─────────────────────────────────────────────────────────────

class AuthState {
  final bool isAuthenticated;
  final String? token;
  final String? staffId;
  final String? role;
  final String? name;

  const AuthState({
    this.isAuthenticated = false,
    this.token,
    this.staffId,
    this.role,
    this.name,
  });

  AuthState copyWith({
    bool? isAuthenticated,
    String? token,
    String? staffId,
    String? role,
    String? name,
  }) =>
      AuthState(
        isAuthenticated: isAuthenticated ?? this.isAuthenticated,
        token: token ?? this.token,
        staffId: staffId ?? this.staffId,
        role: role ?? this.role,
        name: name ?? this.name,
      );
}

// ─── Auth Notifier ────────────────────────────────────────────────────────────

class AuthNotifier extends StateNotifier<AuthState> {
  final FlutterSecureStorage _storage;

  AuthNotifier(this._storage) : super(const AuthState()) {
    _loadFromStorage();
  }

  Future<void> _loadFromStorage() async {
    final token = await _storage.read(key: 'access_token');
    final role = await _storage.read(key: 'role');
    final staffId = await _storage.read(key: 'staff_id');
    final name = await _storage.read(key: 'name');

    if (token != null) {
      state = AuthState(
        isAuthenticated: true,
        token: token,
        role: role,
        staffId: staffId,
        name: name,
      );
    }
  }

  Future<void> login(String phone, String password, ref) async {
    final dio = ref.read(dioProvider);
    final response = await dio.post('/auth/login', data: {
      'phone': phone,
      'password': password,
    });

    final data = response.data as Map<String, dynamic>;
    final token = data['access_token'] as String;
    final role = data['role'] as String;
    final staffId = data['staff_id'] as String;
    final name = data['name'] as String;

    await _storage.write(key: 'access_token', value: token);
    await _storage.write(key: 'role', value: role);
    await _storage.write(key: 'staff_id', value: staffId);
    await _storage.write(key: 'name', value: name);

    state = AuthState(
      isAuthenticated: true,
      token: token,
      role: role,
      staffId: staffId,
      name: name,
    );
  }

  Future<void> logout() async {
    await _storage.deleteAll();
    state = const AuthState();
  }

  bool hasRole(List<String> roles) => roles.contains(state.role);
}

// ─── Providers ────────────────────────────────────────────────────────────────

final authStateProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(secureStorageProvider));
});
