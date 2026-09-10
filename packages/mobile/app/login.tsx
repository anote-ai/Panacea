import React, { useState } from "react";
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, Alert, ScrollView
} from "react-native";
import { router } from "expo-router";
import { useAppTheme, useAppAuth } from "./_layout";
import OurogenLogo from "../src/components/OurogenLogo";
import { login } from "../src/api";

export default function LoginScreen() {
  const { theme, dark, toggle } = useAppTheme();
  const { login: doLogin } = useAppAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (loading) return;
    if (!email.trim() || !password) { Alert.alert("Complete your details", "Enter your email address and password to continue."); return; }
    setLoading(true);
    try {
      const token = await login(email, password);
      await doLogin(token);
      router.replace("/chat");
    } catch (e: any) {
      Alert.alert("Error", e.response?.data?.error ?? "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={[styles.container, { backgroundColor: theme.background }]}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <TouchableOpacity style={styles.themeToggle} onPress={toggle} accessibilityRole="button" accessibilityLabel="Toggle appearance">
        <Text style={{ fontSize: 14, color: theme.text }}>{dark ? "Light" : "Dark"}</Text>
      </TouchableOpacity>
      <ScrollView contentContainerStyle={styles.inner} keyboardShouldPersistTaps="handled">
        <OurogenLogo size={56} dark={dark} />
        <Text accessibilityRole="header" style={[styles.title, { color: theme.text }]}>Welcome back</Text>
        <TextInput
          style={[styles.input, { backgroundColor: theme.inputBg, color: theme.text, borderColor: theme.border }]}
          placeholder="Email"
          accessibilityLabel="Email address"
          autoComplete="email"
          placeholderTextColor={theme.textMuted}
          keyboardType="email-address"
          autoCapitalize="none"
          value={email}
          onChangeText={setEmail}
        />
        <TextInput
          style={[styles.input, { backgroundColor: theme.inputBg, color: theme.text, borderColor: theme.border }]}
          placeholder="Password"
          accessibilityLabel="Password"
          autoComplete="current-password"
          placeholderTextColor={theme.textMuted}
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />
        <TouchableOpacity
          style={[styles.button, { backgroundColor: theme.sendButton }]}
          onPress={submit}
          accessibilityRole="button"
          accessibilityState={{ disabled: loading, busy: loading }}
          disabled={loading}
        >
          <Text style={[styles.buttonText, { color: theme.sendButtonText }]}>
            {loading ? "Signing in..." : "Sign in"}
          </Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => router.push("/register")}>
          <Text style={[styles.link, { color: theme.textMuted }]}>
            Don't have an account? <Text style={{ color: theme.text, fontWeight: "600" }}>Sign up</Text>
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  themeToggle: { position: "absolute", top: 56, right: 20, zIndex: 10 },
  inner: { flexGrow: 1, paddingVertical: 100, justifyContent: "center", alignItems: "center", paddingHorizontal: 32, gap: 16 },
  title: { fontSize: 24, fontWeight: "600", marginTop: 16, marginBottom: 8 },
  input: {
    width: "100%", paddingHorizontal: 16, paddingVertical: 14,
    borderRadius: 12, borderWidth: 1, fontSize: 15,
  },
  button: {
    width: "100%", paddingVertical: 14, borderRadius: 12,
    alignItems: "center",
  },
  buttonText: { fontSize: 15, fontWeight: "600" },
  link: { fontSize: 13, marginTop: 8 },
});
