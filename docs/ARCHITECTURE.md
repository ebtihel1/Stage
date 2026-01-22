finvestrack/
├── apps/
│   ├── users/              # Authentification JWT
│   │   ├── models.py       # User (hérite de AbstractUser)
│   │   ├── views.py        # Login, Register, Profile
│   │   ├── serializers.py  # Validation des données
│   │   └── urls.py         # Routes auth
│   │
│   └── portfolio/          # Gestion des actifs
│       ├── models.py       # Asset (Stock, Bond, Crypto)
│       ├── views.py        # CRUD actifs + Résumé
│       ├── serializers.py  # Validation actifs
│       ├── urls.py         # Routes portfolio
│       └── services/       # Logique métier
│           ├── interfaces.py        # Contrats (interfaces)
│           ├── calculators.py       # Strategy Pattern
│           ├── asset_factory.py     # Factory Pattern
│           ├── repositories.py      # Repository Pattern
│           └── portfolio_service.py # Service métier
│
└── config/                 # Configuration Django
    ├── settings.py         # Variables globales
    └── urls.py             # Routage principal