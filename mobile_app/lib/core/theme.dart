import 'package:flutter/material.dart';

class AppTheme {
  static const Color primaryGold = Color(0xFFD4AF37);
  static const Color primaryDark = Color(0xFF1A1A2E);
  static const Color accentGold = Color(0xFFF5C518);
  static const Color surfaceLight = Color(0xFFFAF9F6);
  static const Color errorRed = Color(0xFFE53935);
  static const Color successGreen = Color(0xFF43A047);

  static ThemeData get lightTheme => ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: primaryGold,
          primary: primaryGold,
          secondary: primaryDark,
          surface: surfaceLight,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: primaryDark,
          foregroundColor: primaryGold,
          centerTitle: true,
          elevation: 0,
        ),
        cardTheme: CardTheme(
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: primaryGold,
            foregroundColor: primaryDark,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
          filled: true,
          fillColor: Colors.grey.shade50,
        ),
        chipTheme: ChipThemeData(
          backgroundColor: primaryGold.withOpacity(0.1),
          labelStyle: const TextStyle(color: primaryDark),
        ),
      );

  static ThemeData get darkTheme => ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: primaryGold,
          brightness: Brightness.dark,
          primary: primaryGold,
        ),
      );
}
