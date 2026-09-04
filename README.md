# fusion-altstore-source

Automatically updated AltStore/SideStore source for [Fusion](https://github.com/yodaluca23/Fusion-AltStore) by yodaluca23.

A daily GitHub Actions workflow (`.github/workflows/update.yml`) checks the upstream repo's releases, downloads the new `Fusion-unsigned-ios.ipa` if needed, reads its `Info.plist`, and updates `fusion.json` according to the [AltStore source schema](https://faq.altstore.io/altstore-2/creating-your-own-altstore-source).

## Add to SideStore/AltStore

Add this source in SideStore or AltStore:

```
https://raw.githubusercontent.com/sti000en/fusion-altstore-source/main/fusion.json
```

## Note

Fusion requires **iOS 26.0 or newer**.
