# External Terminal Feature

## Feature Overview

The External Terminal is a physical interactive component that complements the main Punch Card Project display. It allows gallery visitors to type messages that will be displayed on the main punch card installation, while providing a tangible receipt as confirmation and memento of their participation.

## 1. System Architecture Blueprint

```
┌────────────────────────────────────────────────────────────────────┐
│                  PUNCH CARD INSTALLATION ECOSYSTEM                  │
└────────────────────────────────────────────────────────────────────┘
                                │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
┌─────────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   MAIN PUNCH CARD   │ │ TERMINAL STATION │ │ ADMIN INTERFACE │
│     DISPLAY UNIT    │◄┼►│  (USER INPUT)   │ │  (MONITORING)   │
└─────────────────────┘ └─────────────────┘ └─────────────────┘
      │         ▲             │      ▲             │      ▲
      │         │             │      │             │      │
      ▼         │             ▼      │             ▼      │
┌─────────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   LOCAL DATABASE    │ │ RECEIPT PRINTER  │ │  CONFIGURATION  │
│ ┌───────────────┐   │ │                  │ │    STORAGE      │
│ │ Message Queue │   │ │  ┌───────────┐   │ │                 │
│ │ Schedule Data │   │ │  │ Print Job │   │ │  ┌───────────┐  │
│ │ System Logs   │   │ │  │  Buffer   │   │ │  │ Settings  │  │
│ └───────────────┘   │ │  └───────────┘   │ │  │ Templates │  │
└─────────────────────┘ └─────────────────┘ └─────────────────┘
```

## 2. Hardware Components Breakdown

### Main Punch Card Display Unit
- **Processor**: Raspberry Pi 4 (4GB RAM)
- **Display**: Custom LED matrix (12×80 grid to match punch card rows/columns)
- **Power**: Dedicated power supply with UPS backup
- **Networking**: Built-in WiFi + Ethernet backup
- **Enclosure**: Wooden case with acrylic front panel, designed to recall vintage punch card readers
- **Audio**: Small speakers for mechanical sound effects (optional)

### Terminal Station
- **Processor**: Raspberry Pi 3B+ (or 4)
- **User Interface**: 7-inch touchscreen display in portrait orientation
- **Input Methods**: Virtual keyboard + optional physical keyboard
- **Receipt Printer**: Epson TM-T20 thermal printer (USB connected)
- **Enclosure**: Custom wooden enclosure with vintage IBM aesthetic
  - Angled screen for easy viewing
  - Receipt slot with custom "punch card" themed bezel
  - Potentially hinged keyboard section
- **Power**: Wall power with cable management

### Networking Infrastructure
- **Primary Connection**: Dedicated private WiFi network
  - Main Punch Card as access point
  - Terminal connects as client
- **Backup Connection**: Direct Ethernet cable
- **Security**: WPA2 encryption, hidden SSID, MAC filtering

## 3. Communication Protocol Design

### Primary Protocol: RESTful API over HTTP
```
┌──────────────────┐                        ┌──────────────────┐
│  Terminal Unit   │                        │  Main Punch Card │
└───────┬──────────┘                        └────────┬─────────┘
        │                                            │
        │ ┌────────────────────────────────┐        │
        │ │          API ENDPOINTS         │        │
        │ └────────────────────────────────┘        │
        │                                            │
        │ POST /api/messages                         │
        │ ─────────────────────────────────────────► │
        │ (Submits new message with attributes)      │
        │                                            │
        │ 201 Created                                │
        │ ◄───────────────────────────────────────── │
        │ (Returns message ID, scheduled time)       │
        │                                            │
        │ GET /api/messages/{id}                     │
        │ ─────────────────────────────────────────► │
        │ (Retrieves status of specific message)     │
        │                                            │
        │ 200 OK                                     │
        │ ◄───────────────────────────────────────── │
        │ (Returns message details, status)          │
        │                                            │
        │ GET /api/schedule                          │
        │ ─────────────────────────────────────────► │
        │ (Gets upcoming message schedule)           │
        │                                            │
        │ 200 OK                                     │
        │ ◄───────────────────────────────────────── │
        │ (Returns scheduled message list)           │
        │                                            │
```

### Backup Protocol: Direct Socket Connection
- Fallback for when HTTP communication fails
- Simpler commands with less overhead

### Health Monitoring
- Heartbeat signals every 30 seconds
- Automatic reconnection attempts if connection drops
- Status logging to local database

## 4. User Experience Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER JOURNEY                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ 1. APPROACH │──►   2. TYPE   │──►  3. SUBMIT  │──►  4. RECEIVE │──► 5. OBSERVE  │
│  TERMINAL   │  │   MESSAGE   │  │  & CONFIRM  │  │   RECEIPT   │  │  DISPLAY    │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
      │                │                │                │                │
      ▼                ▼                ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Welcome     │  │ Character   │  │ Preview     │  │ Receives    │  │ Returns to  │
│ screen with │  │ limit with  │  │ screen with │  │ printed     │  │ display at  │
│ animated    │  │ real-time   │  │ confirm or  │  │ receipt     │  │ scheduled   │
│ punch card  │  │ character   │  │ edit button │  │ showing     │  │ time to see │
│ motif and   │  │ count and   │  │ Optional:   │  │ message and │  │ message     │
│ "Touch to   │  │ suggested   │  │ email entry │  │ display time│  │ displayed   │
│ Begin"      │  │ length      │  │ for alert   │  │ in punch    │  │ on large    │
│             │  │             │  │             │  │ card format │  │ display     │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```

## 5. Receipt Design Specification

### Physical Specifications
- **Paper Width**: 80mm (standard thermal receipt paper)
- **Print Resolution**: 203 DPI (standard for Epson TM-T20)
- **Length**: Variable based on message length, ~15-20cm typical
- **Paper Type**: Standard thermal receipt paper
  - Option: Custom pre-printed paper with light punch card pattern background

### Visual Design Elements
```
┌───────────────────────────────────────────────────┐
│        PUNCH CARD PROJECT - MESSAGE RECEIPT       │
│                                                   │
│ ┌───────────────────────────────────────────────┐ │
│ │      Message successfully scheduled!          │ │
│ └───────────────────────────────────────────────┘ │
│                                                   │
│ YOUR MESSAGE:                                     │
│ "Hello from the art gallery"                      │
│                                                   │
│ WILL BE DISPLAYED AT:                             │
│ 3:45 PM TODAY (March 5, 2024)                     │
│                                                   │
│ ┌───────────────────────────────────────────────┐ │
│ │ 12│□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ │
│ │ 11│□□□□□□□□□□□□□□■□□□□□□■□□□□□□□□□□□□□□□□□□□□│ │
│ │  0│□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ │
│ │  1│□□■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ │
│ │  2│□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ │
│ │  3│□□□□□□□■□□□□■□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ │
│ │  4│□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ │
│ │  5│□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ │
│ │  6│□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ │
│ │  7│□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ │
│ │  8│□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ │
│ │  9│□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□□│ │
│ │   └─────────────────────────────────────────┘   │ │
│ │   0123456789012345678901234567890123456789...   │ │
│ │   1         2         3         4         ...   │ │
│ └───────────────────────────────────────────────┘ │
│                                                   │
│ MESSAGE ID: #B52C                                 │
│                                                   │
│ ┌───────────────────────────────────────────────┐ │
│ │      DO NOT FOLD, SPINDLE, OR MUTILATE        │ │
│ └───────────────────────────────────────────────┘ │
│                                                   │
│ THANK YOU FOR PARTICIPATING IN THE PUNCH CARD     │
│ PROJECT. THIS RECEIPT IS YOUR CONFIRMATION THAT   │
│ YOUR MESSAGE HAS BEEN SCHEDULED FOR DISPLAY.      │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Special Details
- **Historical Watermark**: Subtle IBM 026 keypunch machine silhouette as background
- **Authentic Touches**: 
  - Vintage computing font
  - Perforated paper edge design
  - IBM punch card stock reference number

## 6. Data Schema & Message Queue System

### Message Object Structure
```json
{
  "message_id": "B52C",
  "content": "Hello from the art gallery",
  "submitted_at": "2024-03-05T15:23:45Z",
  "scheduled_display_time": "2024-03-05T15:45:00Z",
  "duration_seconds": 60,
  "status": "scheduled",
  "priority": 2,
  "contact_email": "visitor@example.com",
  "terminal_id": "term_01",
  "punch_pattern": [
    [11, 14], [11, 19], [1, 2], [3, 7], [3, 12]
    // Additional punch coordinates
  ]
}
```

### Queue Processing System
- **Priority Levels**:
  1. System Messages (hourly time display, gallery announcements)
  2. Special Event Messages (curator selections, VIP submissions)
  3. Standard Visitor Messages (first-come, first-served)
  
- **Scheduling Algorithm**:
  - Messages scheduled at next available slot based on priority
  - Minimum 60-second display time per message
  - Option to batch similar-priority messages for efficiency
  - Hourly time display takes precedence at :00 of each hour

## 7. Gallery Installation Considerations

### Physical Setup
```
┌──────────────────────────────────────────────────────────────┐
│                      GALLERY FLOOR PLAN                       │
└──────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                                                               │
│                 ┌───────────────────────┐                     │
│                 │                       │                     │
│                 │  MAIN PUNCH CARD      │                     │
│                 │  DISPLAY              │                     │
│                 │                       │                     │
│                 └───────────────────────┘                     │
│                                                               │
│                                                               │
│                                                               │
│    ┌────────────┐                            ┌────────────┐   │
│    │            │                            │            │   │
│    │  TERMINAL  │                            │ HISTORICAL │   │
│    │  STATION   │                            │ ARTIFACTS  │   │
│    │            │                            │            │   │
│    └────────────┘                            └────────────┘   │
│                                                               │
│                                                               │
│    ┌─────────────────────────────────────────────────────┐    │
│    │                                                     │    │
│    │              EXPLANATORY WALL PANEL                 │    │
│    │                                                     │    │
│    └─────────────────────────────────────────────────────┘    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Power & Connectivity Requirements
- **Power**: 
  - Dedicated circuits for main display and terminal
  - UPS backup for both systems
  - Hidden cable management

- **Network**:
  - Self-contained system with private WiFi
  - Ethernet backup cables hidden in walls/floor
  - No dependence on gallery WiFi

- **Maintenance Access**:
  - Service panels on back of both devices
  - Quick-access reboot buttons hidden from general view
  - USB ports for diagnostic access

## 8. Reliability & Fault Tolerance Design

### Failure Modes & Recovery
```
┌────────────────────────────────────────────────────────────────────┐
│                   FAILURE MODE ANALYSIS & RECOVERY                  │
└────────────────────────────────────────────────────────────────────┘

SCENARIO: Power Loss to Terminal Station
  │
  ├── DETECTION: Power monitoring circuit
  │
  ├── IMMEDIATE ACTIONS:
  │   ├── Graceful shutdown of software
  │   └── Alert sent to main display if possible
  │
  ├── RECOVERY:
  │   ├── Auto-restart on power restoration
  │   ├── Database integrity check
  │   └── Reconnect to main display
  │
  └── USER EXPERIENCE:
      ├── Welcome screen with "Restarting" message
      └── Normal operation resumes without user intervention

SCENARIO: Network Communication Failure
  │
  ├── DETECTION: Failed heartbeat or timeout on API calls
  │
  ├── IMMEDIATE ACTIONS:
  │   ├── Log error to local storage
  │   ├── Try alternative communication method
  │   └── Update UI to show "Reconnecting" status
  │
  ├── RECOVERY:
  │   ├── Automatic connection retry with exponential backoff
  │   ├── Switch to backup connection method (WiFi→Ethernet)
  │   └── Sync message queue when connection restored
  │
  └── USER EXPERIENCE:
      ├── Terminal: "Temporarily Unavailable" message
      └── Local operation continues with message caching

SCENARIO: Printer Failure
  │
  ├── DETECTION: Error response from printer driver
  │
  ├── IMMEDIATE ACTIONS:
  │   ├── Log error details
  │   ├── Try printer reset sequence
  │   └── Update UI to show printer status
  │
  ├── RECOVERY:
  │   ├── Offer digital receipt option
  │   ├── Store message in queue regardless of receipt
  │   └── Auto-retry printing when printer available
  │
  └── USER EXPERIENCE:
      ├── Error message with alternative options
      └── Digital receipt via email or QR code for tracking
```

## 9. Historical Authenticity Elements

For true authenticity, incorporate these historical elements from actual IBM punch card systems:

### Terminal Design Touchpoints
- **IBM 026 Keypunch Styling**: 
  - Two-tone color scheme (IBM blue-gray and lighter gray)
  - Beveled keyboard area
  - Round-cornered rectangular keys
  - Function key row with distinct coloring

- **Card Handling Elements**: 
  - Card entry slot styling (even if non-functional)
  - Stacker-inspired receipt output area
  - Program drum dial replica (could be repurposed as volume control)

- **Original Typography**:
  - IBM Plex Mono font family for authentic IBM look
  - ALL CAPS for system messages as was common
  - Original IBM warning language for authenticity

### Authentic Receipt Details
The receipts should include these authentic IBM punch card elements:

- **IBM Card Stock References**: 
  - "IBM 5081" stock number reference
  - Edge printing with authentic "C F 10125" reference codes

- **Authentic Markings**:
  - "IBM" watermark in corner
  - Row/column numbering in correct IBM style
  - "REPRODUCED FROM IBM PUNCHED CARD" disclaimer

- **Archival Elements**:
  - 80-column limitation (truncate or wrap longer messages)
  - Character encoding following actual IBM 026 restrictions
  - Correct row/column notation (12-row, 80-column layout)

## 10. Implementation Timeline & Phasing

For a gallery-ready system, phase the implementation:

### Phase 1: Core Function (4-6 weeks)
- Basic terminal hardware setup
- Fundamental communication between systems
- Simple receipt printing capability
- Message display on main punch card

### Phase 2: Refinement (3-4 weeks)
- Styled enclosures for both components
- Enhanced receipt design
- Improved user interface
- Error handling and recovery systems

### Phase 3: Polish (2-3 weeks)
- Historical authenticity elements
- Sound effects and peripheral details
- Gallery installation planning
- Documentation and maintenance guides

### Phase 4: Testing & Hardening (2 weeks)
- Extended durability testing
- User testing with gallery staff
- Final adjustments and optimization
- Installation documentation for gallery technicians

## 11. Component Shopping List

### Terminal Hardware Components
- Raspberry Pi 4 (4GB RAM)
- 7" Official Raspberry Pi Touchscreen Display
- Epson TM-T20III Thermal Receipt Printer
- Custom wooden enclosure materials
  - Baltic birch plywood (1/4" and 1/2")
  - Blue-gray paint (IBM color match)
  - Clear coat finish
- 12V 5A Power Supply
- MicroSD Card (32GB)
- 80mm Thermal Receipt Paper (multiple rolls)
- Ethernet Cable (Cat6, 25ft)
- Keycap set for optional physical keyboard
- Cable management supplies

### Main Display Add-ons for Integration
- WiFi Access Point module (or dedicated router)
- Network switch (for multi-device connectivity)
- Additional USB ports (hub)
- Local database storage (SSD)

### Tools & Development Components
- USB-Serial adapter (for debugging)
- Logic analyzer (for printer communication troubleshooting)
- Development breadboard for prototyping
- Extra Raspberry Pi for development
- Test LED matrix
- Spare receipt printer (if budget allows)

## 12. Software Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   SOFTWARE ARCHITECTURE                     │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                   TERMINAL STATION                          │
└────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────┼────────────────────────────────┐
│                         │                                │
▼                         ▼                                ▼
┌────────────────┐  ┌────────────────┐     ┌────────────────┐
│  UI SUBSYSTEM  │  │ COMMUNICATION  │     │ RECEIPT HANDLER │
└────────┬───────┘  │   SUBSYSTEM    │     └───────┬────────┘
         │          └───────┬────────┘             │
         ▼                  ▼                      ▼
┌────────────────┐  ┌────────────────┐     ┌────────────────┐
│ React Frontend │  │ API Client     │     │ Printer Driver │
│                │  │                │     │                │
│ - Input Forms  │  │ - REST Client  │     │ - ESC/POS Cmds │
│ - Validation   │  │ - Retry Logic  │     │ - Paper Sizing │
│ - Animation    │  │ - Socket Fallb │     │ - Error Handl. │
│ - User Flow    │  │ - Encryption   │     │ - Buffer Mgmt  │
└────────────────┘  └────────────────┘     └────────────────┘
         │                  │                      │
         └──────────────────┼──────────────────────┘
                           │
                           ▼
                   ┌────────────────┐
                   │  DATA LAYER    │
                   │                │
                   │ - SQLite DB    │
                   │ - Local Cache  │
                   │ - Config Files │
                   │ - Message Queue│
                   └────────────────┘
```

## 13. Message Processing Pipeline

```
┌────────────────────────────────────────────────────────────────────┐
│                   MESSAGE PROCESSING PIPELINE                       │
└────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   
  │ User enters │     │   Input     │     │  Message    │   
  │  message at │────►│ validation  │────►│ conversion  │──┐
  │  terminal   │     │   rules     │     │ to punches  │  │
  └─────────────┘     └─────────────┘     └─────────────┘  │
                                                           │
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
  │  Receipt    │     │   Receipt   │     │  Preview    │  │
  │ generation  │◄────│   design    │◄────│ generation  │◄─┘
  │  & print    │     │  template   │     │             │
  └─────────────┘     └─────────────┘     └─────────────┘
        │                                        │
        │                                        │
        ▼                                        ▼
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │  Network    │     │  Message    │     │ Scheduling  │
  │ transmission│────►│  queueing   │────►│  algorithm  │
  │  to display │     │  system     │     │             │
  └─────────────┘     └─────────────┘     └─────────────┘
                                                 │
                                                 │
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │ Main display│     │   Display   │     │ Scheduled   │
  │  shows the  │◄────│  rendering  │◄────│  message    │
  │   message   │     │   engine    │     │ retrieval   │
  └─────────────┘     └─────────────┘     └─────────────┘
```

## 14. Research: Similar Art Installations

### Case Studies of Relevant Art Installations

1. **"Telegraphic" by Rafael Lozano-Hemmer**
   - Interactive installation where visitors' messages appear on a telegraph-inspired display
   - Uses thermal printers for receipts with historical styling
   - Key insight: Robust message queuing system to handle high volume during exhibitions

2. **"Text Rain" by Camille Utterback & Romy Achituv**
   - Interactive installation where text falls like rain and responds to viewers
   - Uses custom hardware with high reliability for public display
   - Key insight: Fault tolerance and automatic recovery were critical for long-term installation

3. **"Subway Stories" by Ben Rubin & Mark Hansen**
   - Public art piece that displays messages collected from transit users
   - Uses industrial hardware for reliability
   - Key insight: Modular design allowed components to fail independently without taking down entire system

### Key Learnings for Punch Card Project

- **Reliability Focus**: Public installations need automatic recovery from all failure modes
- **Modularity**: Independent components that can function separately
- **Content Management**: Needs filters and moderation for public submission
- **User Experience**: Balance between historical authenticity and modern usability
- **Maintenance Access**: Gallery staff needs simple troubleshooting capabilities

## 15. Future Expansion Possibilities

For future versions, consider these expansion options:

- **Multi-Terminal Support**: Allow multiple input terminals throughout gallery
- **Mobile Integration**: QR code to submit messages from personal devices
- **Archival Feature**: Website displaying historical record of all messages
- **Interactive History**: Digital exploration of punch card history
- **Physical Card Integration**: Option to produce actual punch cards
- **Sentiment Analysis**: Visual effects based on message sentiment
- **Translation Support**: Allow messages in multiple languages 