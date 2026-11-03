Phase 1 fresh-download validation findings

- Data fetched directly from Yahoo Finance for this workspace. Raw files: 5,069 rows each for GS, SPY, XLF; timestamps aligned with no join loss.
- Provider returned Dec 6, 2023–Nov 2, 2026 despite `period=729d`. Raw files remain intact. The dataset restricts modeling to the most recent two 365-day eras: Year 1 1,731 bars; Year 2 1,739 bars after the 30-row warm-up.
- No duplicate timestamps, ordering issues, NaNs, invalid OHLC ranges, or GS zero-volume bars.
- Short/partial days: Jul 3, Nov 29, Dec 24 early-close days; Jan 30, 2026 has only a 09:30 bar and Feb 2 has only 13:30, 14:30, 15:30. The incomplete days are retained and flagged.
- SPY zero-volume rows: 2023-12-12 14:30, 2024-07-26 14:30, 2024-08-01 12:30 ET. XLF zero-volume row: 2024-09-27 13:30 ET. These context-source anomalies are retained and flagged.
- Unadjusted prices are used; ex-dividend dates can appear as small drops in the overnight gap.
