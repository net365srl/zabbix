# Template Zabbix 7.4 — HP / Aruba 2530 family by SNMP

**File:** `zabbix_7.4_hp_2530_full_mibs_v5.yaml`
**Nome template:** `HP Aruba 2530 by SNMP`
**Gruppo:** `Templates/Network devices`
**Tag template:** `class: network`, `target: hp`, `target: hp-enterprise`
**Versione export:** Zabbix `7.4`

Template SNMP per switch **fissi** della famiglia HP/Aruba 2530 (J9772A–J9783A, J9853A–J9856A, JL070A). Deriva dal template 5406 ma è adattato a hardware non modulare e include monitoraggio di **CPU, memoria e stato ambientale**.

---

## 1. Requisiti e setup

1. **Interfaccia SNMP** sull'host (SNMPv2c o SNMPv3), IP/DNS coerente con l'indirizzo sorgente dei trap.
2. Per i **trap** serve la catena `snmptrapd` → receiver → file → *SNMP trapper* di Zabbix. Senza di essa gli item trap non ricevono dati (il polling funziona lo stesso).
3. Polling basato su OID numerici: le MIB servono solo a `snmptrapd`. Caricare `hpicfOid.mib` per primo.

### Macro

| Macro | Default | Uso |
|---|---|---|
| `{$IFCONTROL}` | `1` | Abilita il trigger link-down per interfaccia; `{$IFCONTROL:"porta"}=0` per silenziare porte. |
| `{$HP.CPU.HIGH}` | `85` | Soglia (%) del trigger CPU elevata. |

### Value map incluse
- `IF-MIB::ifOperStatus`
- `HP-ICF::HA failure reason`
- `HP-ICF::Enabled status`
- `HP-ICF::Sensor status` (1=unknown/invalid, 2=bad, 3=warning, 4=good, 5=notPresent)

---

## 2. Cosa monitora (polling SNMP)

### Sistema
| Item | Note |
|---|---|
| System name / description / location / contact / object ID | Inventario base. |
| System uptime | **Trigger:** *Switch has been restarted* (Warning) se uptime < 10 min. |
| SNMP availability check | Raggiungibilità agent. |

### Throughput aggregato
`net.if.total.in`, `net.if.total.out`, `net.if.total` — somma inbound/outbound/totale delle interfacce scoperte.

### Salute hardware (specifica 2530) — **NOVITÀ rispetto al 5406**
| Item | OID | Note |
|---|---|---|
| **CPU utilization** | `1.3.6.1.4.1.11.2.14.11.5.1.9.6.1.0` | %. **Trigger:** *High CPU utilization* (Warning) se media 5 min > `{$HP.CPU.HIGH}`. |
| **Free memory** | `1.3.6.1.4.1.11.2.14.11.5.1.1.2.1.1.1.6.1` | Byte. |
| **Fan state** | `…11.1.2.6.1.4.1` | Value-mapped `HP-ICF::Sensor status`. |
| **PSU primary** | `…11.1.2.6.1.4.2` | Value-mapped. |
| **PSU secondary** | `…11.1.2.6.1.4.3` | Value-mapped. |
| **Temperature state** | `…11.1.2.6.1.4.4` | Value-mapped. |

### Vendor HP (routing / SNMP)
| Item | Note |
|---|---|
| IP routing: Total route count | Numero rotte attive. |
| IP routing: ARP aging time | Minuti. |
| SNMP: Authorization notification enabled | Stato `hpicfSnmpAuthNotifyEnable`. |

---

## 3. Discovery (LLD)

### `net.if.discovery` — Interfacce (IF-MIB)
Per porta: stato operativo, traffico in/out (HC → bps), errori in/out, discard in/out, velocità, alias. Include graph prototype `Interface {#IFNAME}: Bandwidth`.

- **Trigger prototype:** *Interface {#IFNAME}: Link down* — **Information** — solo su transizione up→non-up, auto-close **2h**, silenziabile con `{$IFCONTROL}`.

> ℹ️ A differenza del 5406, **non** è presente la discovery CPU per modulo: il 2530 è uno switch fisso e la CPU è esposta come **item globale** (vedi §2).

---

## 4. Trap SNMP (58 item, 42 con trigger)

Struttura identica al template 5406, con l'unica differenza dell'item RMON di modello.

### RMON di modello — famiglia 2530
- **`SNMP traps: HP 2530 family RMON event`** riconosce i trap dei modelli J9772A–J9783A, J9853A–J9856A, JL070A (nomi simbolici **e** rami OID `…3.7.11.<id>.0.2`).

### Standard
coldStart (Warning/2h), warmStart (Warning/2h), linkDown/linkUp (log), **authenticationFailure** (Average/48h — solo il vero OID `1.3.6.1.6.3.1.1.5.5`).

### Chassis / alimentazione / sensori
HP sensor bad (High), HP sensor warning (Average), HP power supply faulted (High), HP power supply removed (Average) + varianti generiche in log.

### Fault Finder — **tutti i 42 tipi**
Stessa copertura e stesse severità/policy del 5406; auto-close 48h.

### Autenticazione / accesso
- **`HP management authentication failure`** (Average/48h): login errati su **WEB-UI / SSH / TELNET** via evento RMON HP (testo `auth: Invalid user name/password on … session`).
- **`authenticationFailure`** standard: separato, solo trap SNMP protocollare.

### Fallback
- **`snmptrap.fallback`** per gli eventi non classificati.

---

## 5. Cosa **NON** funziona / limitazioni note

- **CPU / memoria / ventola / PSU / temperatura sono ABILITATI**, ma il supporto dipende da **modello e firmware** 2530. Se un OID non è implementato, l'item diventa `Not supported` (`No Such Object`) e va disabilitato sul singolo host/template. **Verificare con `snmpget` prima di dare per scontata la metrica** (vedi §7).
- **Nessun monitoraggio HA/OSPF vendor** (rimosso rispetto al 5406): sono funzioni da chassis modulare non pertinenti al 2530 fisso.
- **Trap:** richiedono `snmptrapd` + receiver configurati.
- **Severità Fault Finder:** policy operativa, non mappatura ufficiale MIB.
- **Copertura MIB:** il template usa OID standard per il polling e regex simbolico/numerico per i trap. La **presenza di una MIB nella cartella sorgente non garantisce** che ogni oggetto sia implementato da ogni variante 2530; oggetti non supportati emergeranno come `No Such Object`.

---

## 6. Dashboard inclusa — *HP 2530 - Operations* (3 pagine)

| Pagina | Contenuto |
|---|---|
| **Overview** | Nome/ubicazione/uptime/SNMP · CPU · memoria libera · ventola · temperatura · PSU 1/2 · rotte · ARP · grafico throughput in/out · widget **Problemi correnti**. |
| **Performance** | Trend CPU · trend memoria libera · griglia banda per-interfaccia (in+out) · griglia errori in ingresso per porta. |
| **Environment & health** | Ventola · PSU 1/2 · temperatura · trend CPU · trend memoria · descrizione sistema. |

---

## 7. Verifica rapida post-import

```bash
# CPU globale (deve restituire 0-100)
snmpget  -v2c -c COMMUNITY IP 1.3.6.1.4.1.11.2.14.11.5.1.9.6.1.0
# memoria libera (byte)
snmpget  -v2c -c COMMUNITY IP 1.3.6.1.4.1.11.2.14.11.5.1.1.2.1.1.1.6.1
# stati ambientali (fan/psu/temp)
snmpwalk -v2c -c COMMUNITY IP 1.3.6.1.4.1.11.2.14.11.1.2.6.1.4
# interfacce (throughput HC)
snmpwalk -v2c -c COMMUNITY IP 1.3.6.1.2.1.31.1.1.1.6
```
Se un `snmpget` risponde `No Such Object`, disabilitare il relativo item su quell'host.

---


## 9. Changelog sintetico
- v5: fix widget graph-prototype (`ITEM_PROTOTYPE`/`GRAPH_PROTOTYPE`) — import ora pulito.
- v4: dashboard operativa multi-pagina.
- v3: aggiunti tag `class/target`.
- v2: abilitati CPU, memoria, fan, PSU, temperatura.
- v1: base derivata dal 5406 con RMON famiglia 2530 e rimozione componenti chassis-only.
