# fusion-altstore-source

Automatisch aktualisierte AltStore/SideStore-Quelle für [Fusion](https://github.com/yodaluca23/Fusion-AltStore) von yodaluca23.

Ein täglicher GitHub-Actions-Workflow (`.github/workflows/update.yml`) prüft die Releases des Upstream-Repos, lädt bei Bedarf die neue `Fusion-unsigned-ios.ipa`, liest deren `Info.plist` aus und aktualisiert `fusion.json` nach dem [AltStore-Source-Schema](https://faq.altstore.io/altstore-2/creating-your-own-altstore-source).

## SideStore/AltStore hinzufügen

Quelle in SideStore oder AltStore hinzufügen:

```
https://raw.githubusercontent.com/sti000en/fusion-altstore-source/main/fusion.json
```

## Hinweis

Fusion benötigt **iOS 26.0 oder neuer**.
