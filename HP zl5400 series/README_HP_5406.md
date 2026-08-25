# Template Zabbix 7.4 — HP ProCurve 5406 (zl / zl2) by SNMP

**File:** `zabbix_7.4_hp_5406_vendor_mibs_v17.yaml`
**Nome template:** `HP ProCurve 5406 by SNMP`
**Gruppo:** `Templates/Network devices`
**Tag template:** `class: network`, `target: hp`, `target: hp-enterprise`
**Versione export:** Zabbix `7.4`

Template SNMP per switch modulari HP ProCurve/Aruba serie 5406 (identificatore RMON `hpSwitchJ8697Atrap`, modello J8697A 5406zl). Combina polling di stato/prestazioni, discovery delle interfacce e una classificazione estesa dei trap SNMP.

---

## 1. Requisiti e setup

1. **Interfaccia SNMP** sull'host in Zabbix (SNMPv2c o SNMPv3), IP/DNS corrispondente all'indirizzo sorgente dei trap.
2. Per i **trap** serve la catena `snmptrapd` → receiver (Bash/Perl/SNMPTT) → file trap → *SNMP trapper* di Zabbix. Senza questa catena gli item trap restano `Not supported`/senza dati (gli item di polling funzionano comunque).
3. Le MIB HP non sono necessarie al polling (si usano OID numerici). Sono utili solo a `snmptrapd` per tradurre i nomi simbolici nei trap. Caricare sempre `hpicfOid.mib` prima delle altre MIB HP.

### Macro

| Macro | Default | Uso |
|---|---|---|
| `{$IFCONTROL}` | `1` | Abilita il trigger link-down per interfaccia. Usare la forma contestuale `{$IFCONTROL:"nomePorta"}=0` per silenziare porte volutamente down. |
| `{$HP.MODULE.CPU.HIGH}` | `85` | Soglia (%) per il trigger di CPU elevata dei moduli. |

### Value map incluse
- `IF-MIB::ifOperStatus` (up/down/testing/…)
- `HP-ICF::HA failure reason`
- `HP-ICF::Enabled status`

---

## 2. Cosa monitora (polling SNMP)

### Sistema
| Item | Note |
|---|---|
| System name / description / location / contact / object ID | Inventario base (SNMPv2-MIB). |
| System uptime | **Trigger:** *Switch has been restarted* (Warning) se uptime < 10 min. |
| SNMP availability check | Raggiungibilità dell'agent. |

### Throughput aggregato (calculated items)
| Item | Descrizione |
|---|---|
| `net.if.total.in` | Somma del traffico inbound di tutte le interfacce scoperte. |
| `net.if.total.out` | Somma del traffico outbound. |
| `net.if.total` | Inbound + outbound. |

### Vendor HP (HP-ICF)
| Item | OID base | Note |
|---|---|---|
| HA: Redundancy failure reason | `…1.11.2.1.0` | Value-mapped. |
| HA: Management module failovers | `…1.11.2.2.0` | **Trigger:** *Failover detected* (Warning) se il contatore aumenta. |
| HA: Last failover time | `…1.11.2.3.0` | TimeTicks → uptime. |
| IP routing: Total route count | `…5.1.15.3.1.0` | Numero rotte attive. |
| IP routing: ARP aging time | `…5.1.15.1.6.1.0` | Minuti. |
| SNMP: Authorization notification enabled | `…5.1.38.1.1.1.3.0` | Stato di `hpicfSnmpAuthNotifyEnable`. |
| **OSPF: Reference cost** | `…5.1.14.1.1.11.0` | **⚠️ DISABILITATO di default** — vedi §5. |

---

## 3. Discovery (LLD)

### `net.if.discovery` — Interfacce (IF-MIB)
Per ogni interfaccia crea: stato operativo, traffico in/out (contatori HC a 64 bit → bps), errori in/out, discard in/out, velocità, alias. Include il **graph prototype** `Interface {#IFNAME}: Bandwidth` (in+out).

- **Trigger prototype:** *Interface {#IFNAME}: Link down* — **severità Information** — scatta **solo sulla transizione up→non-up** (non se la porta è scoperta già down). Chiusura automatica dopo **2 ore** se lo stato non torna up (finestra `count(...,2h,"eq",1)`), oppure immediata al ritorno `up`. Silenziabile con `{$IFCONTROL:"porta"}=0`.

### `hp.module.discovery` — CPU dei moduli (HP-ICF-SLOT-STATS-MIB)
Per ogni modulo dello chassis: modello hardware, seriale, CPU corrente %, CPU media %. Adatta allo chassis modulare 5406.

---

## 4. Trap SNMP (58 item, 42 con trigger)

Ogni item usa una regex che riconosce **sia il nome simbolico sia l'OID numerico**, così funziona anche se `snmptrapd` non traduce l'OID.

### Standard (SNMPv2-MIB / IF-MIB)
| Trap | Severità | Auto-close |
|---|---|---|
| coldStart | Warning | 2h |
| warmStart | Warning | 2h |
| linkDown / linkUp | — (solo log) | — |
| **authenticationFailure** | Average | 48h |

> `linkDown/linkUp` sono solo raccolti (nessun problema) per non duplicare il trigger di stato già presente nella LLD interfacce.

### Chassis / alimentazione / sensori (HP-ICF-CHASSIS)
| Trap | Severità |
|---|---|
| HP sensor bad | High |
| HP sensor warning | Average |
| HP power supply faulted | High |
| HP power supply removed | Average |
| (generici) sensor state change / power supply status change | — (log) |

### Fault Finder (HP-ICF-FAULT-FINDER-MIB) — **tutti i 42 tipi**
Un item per ciascun `HpicfFaultType`. Severità assegnate come **policy operativa** (la MIB non mappa staticamente i livelli):
- **High:** network loop, fan fault, RPS fault, loss of stack member, hot-swap reboot, port self-test failure, connection-rate filter blocked, PHY read failure.
- **Average:** transceiver/cavo/bandwidth/storm/loss-of-link/port-security/duplex/jumbo/link-flap ecc.
- **Log (nessun trigger):** badDriver, tooLongCable, misconfiguredSQE, polarityReversal, backupLinkTransition, crfNotify, xcvrCloneReminder, rxNonStdPreamble.

Tutti i trigger Fault Finder si auto-chiudono dopo **48h** senza nuovo evento della stessa categoria.

### Autenticazione / accesso
| Trap | Severità | Auto-close | Cosa intercetta |
|---|---|---|---|
| **HP management authentication failure** | Average | 48h | Login errati su **WEB-UI / SSH / TELNET** (evento RMON HP con testo `auth: Invalid user name/password on … session`). |
| authenticationFailure (standard) | Average | 48h | Solo il vero trap SNMP `1.3.6.1.6.3.1.1.5.5`. |

> ⚠️ **Distinzione importante:** un login fallito alla Web UI **non** genera il trap standard `authenticationFailure`; arriva come evento RMON del modello. Per questo esistono due item separati.

### Fallback
- **`snmptrap.fallback`** — cattura qualunque trap non classificato dagli item specifici. Utile per scoprire eventi firmware non ancora mappati.

---

## 5. Cosa **NON** funziona / limitazioni note

- **OSPF Reference cost — DISABILITATO.** Sul J8697A testato l'agent risponde `No Such Object`. Abilitare solo dopo aver verificato con `snmpget` che il firmware/feature-set esponga l'OID.
- **Item di temperatura "pseudocontainer".** NON sono generati da questo template. Se compaiono sull'host con errore `No Such Object`, provengono da **un altro template collegato** o da una discovery preesistente: vanno disabilitati/scollegati lì.
- **Trap:** senza `snmptrapd` + receiver configurati, gli item trap non ricevono dati (non è un difetto del template).
- **Severità Fault Finder:** sono una proposta operativa, non una mappatura ufficiale della MIB. Adattarle alle proprie policy.
- **Discovery moduli CPU:** valida per chassis modulare; su hardware/firmware che non implementano `HP-ICF-SLOT-STATS-MIB` i prototipi resteranno senza dati.

---

## 6. Dashboard inclusa — *HP 5406 - Operations* (3 pagine)

| Pagina | Contenuto |
|---|---|
| **Overview** | Nome/ubicazione/uptime/disponibilità SNMP · grafico throughput in/out · throughput totale · widget **Problemi correnti**. |
| **Interfaces** | Griglia banda per-interfaccia (graph prototype in+out) · totale inbound/outbound · griglia errori in ingresso per porta. |
| **System & vendor health** | HA (failover/last/reason) · SNMP auth notify · rotte/ARP/OSPF · griglia CPU per modulo · descrizione sistema. |

Le griglie per-interfaccia e per-modulo si popolano automaticamente con la LLD.

---

## 7. Verifica rapida post-import

```bash
# raggiungibilità e system
snmpget  -v2c -c COMMUNITY IP 1.3.6.1.2.1.1.3.0
# throughput di base (deve elencare le interfacce)
snmpwalk -v2c -c COMMUNITY IP 1.3.6.1.2.1.31.1.1.1.6
# OSPF reference cost (se risponde, abilitare l'item)
snmpget  -v2c -c COMMUNITY IP 1.3.6.1.4.1.11.2.14.11.5.1.14.1.1.11.0
```

---

## 8. Changelog sintetico
- v17: dashboard operativa multi-pagina; fix widget graph-prototype (`ITEM_PROTOTYPE`/`GRAPH_PROTOTYPE`).
- v15: aggiunti tag `class/target`.
- v14: item auth WEB-UI/SSH/TELNET separato dal trap SNMP standard.
- v11–v13: copertura completa 42 tipi Fault Finder; rimozione trap custom ridondante; OSPF disabilitato.
- v1–v10: base SNMP, LLD interfacce, throughput, trap standard/vendor, trigger link-down a chiusura 2h.
