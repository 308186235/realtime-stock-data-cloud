ÿþ# ¤Nfû|ß~APIech



## úW@xáOo`



- **Base URL**: `https://api.trading-system.com/v1`

- **¤Á¹e_**: Bearer Token

- **Ø¤ÔÞV<h_**: JSON



## ¤Á



### ·ÖSäNLr



```

POST /auth/token

```



÷BlSO:



```json

{

  "username": "your_username",

  "password": "your_password"

}

```



ÍT^:



```json

{

  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",

  "token_type": "Bearer",

  "expires_in": 3600

}

```



@b  gTí~÷Bl(W4YèS+T:



```

Authorization: Bearer {access_token}

```



## LÅ`penc



### ·ÖS[öeLÅ`



```

GET /market/realtime/{symbol}

```



ÂSpe:



| 
Tðy   | {|W   | Å_kX | Ïcð            |

|--------|--------|------|-----------------|

| symbol | string | /f   | ¡hyãNxÿY SH000001 |



ÍT^:



```json

{

  "symbol": "SH000001",

  "name": "
NÁcpe",

  "price": 3258.63,

  "change": 18.25,

  "changePercent": 0.56,

  "volume": 12345678,

  "turnover": 9876543210,

  "timestamp": 1622345678000

}

```



### ·ÖSK¿~penc



```

GET /market/kline/{symbol}

```



ÂSpe:



| 
Tðy     | {|W   | Å_kX | Ïcð                       |

|----------|--------|------|----------------------------|

| symbol   | string | /f   | ¡hyãNx                   |

| period   | string | &T   | K¿~hTg: 1m, 5m, 15m, 30m, 1h, 1d, 1w, 1M (Ø¤: 1d) |

| startTime | long   | &T   | _ËYöeô3b(ëkÒy)           |

| endTime   | long   | &T   | Ó~_göeô3b(ëkÒy)           |

| limit    | int    | &T   | ÔÞVK¿~peÏ(Ø¤: 100, g'Y: 1000) |



ÍT^:



```json

{

  "symbol": "SH000001",

  "period": "1d",

  "data": [

    {

      "time": 1622345678000,

      "open": 3240.12,

      "high": 3260.45,

      "low": 3235.67,

      "close": 3258.63,

      "volume": 12345678,

      "turnover": 9876543210

    },

    // ôfYK¿~penc...

  ]

}

```



## V{euRg



### ·ÖSUSNV{euRg



```

GET /strategy/analyze/{strategy}/{symbol}

```



ÂSpe:



| 
Tðy     | {|W   | Å_kX | Ïcð                       |

|----------|--------|------|----------------------------|

| strategy | string | /f   | V{euID: sixSword, jiuFang, compass, limitUpDoubleNegative |

| symbol   | string | /f   | ¡hyãNx                   |

| period   | string | &T   | RghTg: 1d, 1w, 1M (Ø¤: 1d) |



ÍT^:



```json

{

  "strategy": "sixSword",

  "symbol": "SH000001",

  "name": "
NÁcpe",

  "timestamp": 1622345678000,

  "overallScore": 70,

  "recommendation": {

    "action": "buy",

    "confidence": "medium",

    "description": "'YèRch>f:yïygáO÷Sÿ^:Wp¿RT}Y0"

  },

  "strategies": {

    "tian": { "score": 60, "interpretation": "  gN[z4xùaÿFOnx¤ÿïS\ÓNMOÕ¢c" },

    "di": { "score": 40, "interpretation": "¡÷N(W/edMO  gHeÍS9_ÿïSý_ËY
N¨m" },

    "ren": { "score": 35, "interpretation": "Ï÷NMTo}Yÿ>eÏ
N¨mÿwYáO÷Sfnx" },

    "he": { "score": 65, "interpretation": "¡÷NteTf>fO3zÞVGSÿïSý/fpNeQ:gO" },

    "shun": { "score": 70, "interpretation": "'Y¿RT
Nÿú^®z¿RÍd\Oÿc¡bpNeQ" },

    "ling": { "score": 55, "interpretation": "èRØ§~ch>f:yïygÿ(NawY" }

  }

}

```



### ·ÖSb_`Æ+RÓ~g



```

GET /strategy/patterns/{symbol}

```



ÂSpe:



| 
Tðy     | {|W   | Å_kX | Ïcð                       |

|----------|--------|------|----------------------------|

| symbol   | string | /f   | ¡hyãNx                   |

| lookback | int    | &T   | ÞV¯nRgvK¿~peÏ (Ø¤: 100) |



ÍT^:



```json

{

  "symbol": "SH000001",

  "timestamp": 1622345678000,

  "summary": {

    "trend": ")nT
N¨m",

    "strength": "-N",

    "recommendation": "(NapNeQ",

    "description": "úQ°sNNw¨máO÷Sÿ^:WïSýHT°s)nT
N¨m¿R"

  },

  "detectedPatterns": [

    {

      "name": "MACDÑÉS",

      "detected": true,

      "confidence": 0.85,

      "direction": "bullish",

      "description": "MACDÑÉS/fN*Nw¨máO÷Sÿhfíwg¨RÏÇg¨RÏ"

    },

    {

      "name": "ÌS^b_`",

      "detected": true,

      "confidence": 0.70,

      "direction": "bullish",

      "description": "ÌS^/fNÍy^èÍSlb_`ÿhfNÌ¿RsS\Ó~_g"

    }

    // ôfYb_`...

  ]

}

```



### ·ÖSYV{euü~TRg



```

GET /strategy/composite/{symbol}

```



ÂSpe:



| 
Tðy     | {|W   | Å_kX | Ïcð                       |

|----------|--------|------|----------------------------|

| symbol   | string | /f   | ¡hyãNx                   |

| strategies | array  | &T   | S+TvV{euIDpeÄ~ (Ø¤: hQèV{eu) |



ÍT^:



```json

{

  "symbol": "SH000001",

  "name": "
NÁcpe",

  "timestamp": 1622345678000,

  "overallScore": 65,

  "decision": {

    "action": "buy",

    "confidence": "medium",

    "allocation": 0.6,

    "description": "'YèRch>f:yïygáO÷Sÿ^:Wp¿RT}Y0"

  },

  "weights": {

    "sixSword": 0.35,

    "jiuFang": 0.35,

    "compass": 0.30

  },

  "strategyResults": {

    "sixSword": { /* mQ ^yQRV{euÓ~g */ },

    "jiuFang": { /* ]N¹ezfbV{euÓ~g */ },

    "compass": { /* cWSV{euÓ~g */ }

  }

}

```



### V{euÞVKm



```

POST /strategy/backtest

```



÷BlSO:



```json

{

  "symbol": "SH000001",

  "strategies": ["sixSword", "jiuFang", "compass"],

  "startDate": "2023-01-01",

  "endDate": "2023-06-30",

  "initialCapital": 100000,

  "positionSizing": "percent",

  "positionPercent": 0.7

}

```



ÍT^:



```json

{

  "symbol": "SH000001",

  "startDate": "2023-01-01",

  "endDate": "2023-06-30",

  "initialCapital": 100000,

  "finalCapital": 125000,

  "totalReturn": 25.0,

  "annualizedReturn": 50.0,

  "maxDrawdown": 10.5,

  "sharpeRatio": 1.8,

  "trades": [

    {

      "date": "2023-02-15",

      "type": "buy",

      "price": 3200.5,

      "shares": 100,

      "strategy": "sixSword"

    },

    {

      "date": "2023-03-20",

      "type": "sell",

      "price": 3300.5,

      "shares": 100,

      "strategy": "compass",

      "profit": 10000,

      "profitPercent": 3.12

    }

    // ôfY¤Nf°U_...

  ],

  "strategyPerformance": {

    "sixSword": {

      "totalReturn": 15.2,

      "winRate": 65.0,

      "profitLossRatio": 2.1

    },

    "jiuFang": {

      "totalReturn": 12.8,

      "winRate": 62.0,

      "profitLossRatio": 1.8

    },

    "compass": {

      "totalReturn": 18.5,

      "winRate": 68.0,

      "profitLossRatio": 2.3

    }

  }

}

```



## AI³QV{û|ß~



### ·ÖSAI³QV{ú^®



```

GET /ai/decision/{symbol}

```



ÂSpe:



| 
Tðy     | {|W   | Å_kX | Ïcð                       |

|----------|--------|------|----------------------------|

| symbol   | string | /f   | ¡hyãNx                   |

| includeDetails | boolean | &T | /f&TS+TæÆ~Rg (Ø¤: false) |



ÍT^:



```json

{

  "symbol": "SH000001",

  "timestamp": 1622345678000,

  "action": "buy",

  "confidence": "high",

  "allocation": 0.7,

  "description": "Y*NV{eu>f:ypNeQáO÷Sÿ^:W¿RT
Nÿú^®Mn70%ÓNMO",

  "keyPoints": [

    "MACDÑÉSáO÷Sfnx",

    "b¤NÏ   gHe>e'Y",

    "÷N<hz4xsQ.;RMO",

    "^:WÅ`ê~OPTPNÂ"

  ],

  "technicalIndicators": [

    {

      "name": "MACD",

      "value": "ÑÉS",

      "trend": "up",

      "significance": "positive"

    },

    {

      "name": "RSI",

      "value": "65.2",

      "trend": "up",

      "significance": "positive"

    }

    // ôfYch...

  ],

  "strategyWeights": {

    "sixSword": 0.35,

    "jiuFang": 0.35,

    "compass": 0.30

  }

}

```



### V{euCgÍte



```

POST /ai/optimize-weights

```



÷BlSO:



```json

{

  "symbol": "SH000001",

  "marketCondition": "bullish", // bullish, bearish, neutral

  "volatility": "medium", // low, medium, high

  "timeHorizon": "medium", // short, medium, long

  "riskTolerance": "medium" // low, medium, high

}

```



ÍT^:



```json

{

  "symbol": "SH000001",

  "optimizedWeights": {

    "sixSword": 0.40,

    "jiuFang": 0.35,

    "compass": 0.25

  },

  "explanation": "úWNS_MR[r^¯sXÿÐcØN¿Rß*V{euCgÍÿMNONGW<PÞVR_V{euCgÍ",

  "expectedPerformance": {

    "estimatedReturn": 15.3,

    "estimatedRisk": 12.4,

    "sharpeRatio": 1.23

  }

}

```



## (u7bpenc



### ·ÖS(u7bV{euMn



```

GET /user/strategy-config

```



ÍT^:



```json

{

  "userId": "user123",

  "defaultStrategies": ["sixSword", "jiuFang", "compass"],

  "strategyParameters": {

    "sixSword": {

      "tianPeriod": 20,

      "diRsiLevel": 30

      // ôfYÂSpe...

    },

    "jiuFang": {

      "patternSensitivity": 0.7

      // ôfYÂSpe...

    },

    "compass": {

      "macdFast": 12,

      "macdSlow": 26

      // ôfYÂSpe...

    }

  },

  "riskProfile": {

    "maxDrawdown": 15,

    "maxAllocation": 80,

    "stopLossPercent": 8

  }

}

```



### ôf°eV{euÂSpe



```

PUT /user/strategy-parameters/{strategy}

```



÷BlSO:



```json

{

  "parameters": {

    "tianPeriod": 25,

    "diRsiLevel": 35

    // ôfYÂSpe...

  }

}

```



ÍT^:



```json

{

  "strategy": "sixSword",

  "success": true,

  "message": "V{euÂSpeôf°ebR",

  "updatedParameters": {

    "tianPeriod": 25,

    "diRsiLevel": 35

    // ôfYÂSpe...

  }

}

```



## ïYt



@b  gAPIïOÔÞVøv^vHTTP¶r`xTJSON<h_vïáOo`:



```json

{

  "error": {

    "code": "INVALID_PARAMETER",

    "message": "àeHev¡hyãNx<h_",

    "details": "¡hyãNx^åNSHbSZ_4YÿTß6MOpeW["

  }

}

```



8^Áïx:



| ¶r`x | ïx | Ïcð |

|--------|--------|------|

| 400 | INVALID_PARAMETER | ÷BlÂSpeàeHe |

| 401 | UNAUTHORIZED | *gcCg¿î |

| 403 | FORBIDDEN | CgP
N³ |

| 404 | NOT_FOUND | Dn*g~b0R |

| 429 | RATE_LIMITED | ÷BlsP |

| 500 | SERVER_ERROR | 
g¡RhVQèï |



## pencP6R



- LÅ`pencôf°es: [öe¥b÷N3Òyôf°eN!k

- API(uP6R: úW@x&7bÏkR100!k÷Bl

- ÞVKmP6R: úW@x&7bÏk)Y10!kÞVKmÿØ§~&7bÏk)Y100!k

- pencSòS: úW@x&7bgY·ÖS3t^SòSpencÿØ§~&7bàeP6R

