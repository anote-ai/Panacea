// macOS signing/notarization and Windows Authenticode signing are opt-in via
// env vars so local/unsigned builds keep working exactly as before. Set these
// in CI (e.g. GitHub Actions secrets) to produce signed release artifacts:
//   macOS:   APPLE_SIGNING_IDENTITY, APPLE_ID, APPLE_ID_PASSWORD (app-specific
//            password), APPLE_TEAM_ID
//   Windows: WINDOWS_CERTIFICATE_FILE (path to .pfx), WINDOWS_CERTIFICATE_PASSWORD
const {
  APPLE_SIGNING_IDENTITY,
  APPLE_ID,
  APPLE_ID_PASSWORD,
  APPLE_TEAM_ID,
  WINDOWS_CERTIFICATE_FILE,
  WINDOWS_CERTIFICATE_PASSWORD,
} = process.env;

const osxSign = APPLE_SIGNING_IDENTITY ? { identity: APPLE_SIGNING_IDENTITY } : undefined;
const osxNotarize =
  APPLE_ID && APPLE_ID_PASSWORD && APPLE_TEAM_ID
    ? { appleId: APPLE_ID, appleIdPassword: APPLE_ID_PASSWORD, teamId: APPLE_TEAM_ID }
    : undefined;
const windowsCertConfig =
  WINDOWS_CERTIFICATE_FILE && WINDOWS_CERTIFICATE_PASSWORD
    ? { certificateFile: WINDOWS_CERTIFICATE_FILE, certificatePassword: WINDOWS_CERTIFICATE_PASSWORD }
    : {};

module.exports = {
  packagerConfig: {
    asar: true,
    name: "Anote AI",
    icon: "./assets/icon",
    extraResource: ["./backend-dist"],
    ...(osxSign ? { osxSign } : {}),
    ...(osxNotarize ? { osxNotarize } : {}),
  },
  rebuildConfig: {},
  makers: [
    { name: "@electron-forge/maker-squirrel", config: { name: "anote_ai", ...windowsCertConfig } },
    { name: "@electron-forge/maker-dmg", config: { format: "ULFO" } },
    { name: "@electron-forge/maker-deb", config: {} },
  ],
  publishers: [
    {
      name: "@electron-forge/publisher-github",
      config: {
        repository: { owner: "anote-ai", name: "Autonomous-Intelligence" },
        prerelease: false,
        draft: true,
      },
    },
  ],
};
