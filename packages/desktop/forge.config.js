// Code signing / notarization is opt-in based on environment variables so that
// local `npm run make` and CI builds without the relevant repo secrets still
// produce unsigned installers exactly as before (see issue #295). Once real
// certificates are provisioned and added as repo secrets, these activate
// automatically — no further code changes needed. See packages/desktop/README.md
// for the exact secret names to add.

const macSigningConfigured = Boolean(
  process.env.APPLE_ID &&
    process.env.APPLE_ID_PASSWORD &&
    process.env.APPLE_TEAM_ID &&
    process.env.APPLE_CERTIFICATE_P12,
);

const winSigningConfigured = Boolean(
  process.env.WINDOWS_CERTIFICATE_FILE && process.env.CSC_KEY_PASSWORD,
);

module.exports = {
  packagerConfig: {
    asar: true,
    name: "Anote AI",
    icon: "./assets/icon",
    extraResource: ["./backend-dist"],
    // @electron/osx-sign picks up the identity imported into the keychain
    // by the CI step in .github/workflows/release.yml; no explicit identity
    // needed here as long as exactly one valid Developer ID cert is present.
    ...(macSigningConfigured
      ? {
          osxSign: {},
          osxNotarize: {
            appleId: process.env.APPLE_ID,
            appleIdPassword: process.env.APPLE_ID_PASSWORD,
            teamId: process.env.APPLE_TEAM_ID,
          },
        }
      : {}),
  },
  rebuildConfig: {},
  makers: [
    {
      name: "@electron-forge/maker-squirrel",
      config: {
        name: "anote_ai",
        ...(winSigningConfigured
          ? {
              certificateFile: process.env.WINDOWS_CERTIFICATE_FILE,
              certificatePassword: process.env.CSC_KEY_PASSWORD,
            }
          : {}),
      },
    },
    { name: "@electron-forge/maker-dmg", config: { format: "ULFO" } },
    { name: "@electron-forge/maker-deb", config: {} },
  ],
  publishers: [
    {
      name: "@electron-forge/publisher-github",
      config: {
        repository: { owner: "anote-ai", name: "Panacea" },
        prerelease: false,
        draft: true,
      },
    },
  ],
};
