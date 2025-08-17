#!/bin/bash

# 修复Coinbase
sed -i '/let crypto_price = CryptoPrice {/,/};/c\
                    let crypto_price = CryptoPrice::new(\
                        symbol.to_string(),\
                        price,\
                        if change_24h.abs() > 50.0 { 0.0 } else { change_24h },\
                        volume_24h,\
                        "coinbase".to_string(),\
                    );' src/exchanges/coinbase.rs

# 修复OKX
sed -i '/Some(CryptoPrice {/,/})/c\
        Some(CryptoPrice::new(\
            symbol.to_string(),\
            price,\
            change_percent,\
            volume,\
            "OKX".to_string(),\
        ))' src/exchanges/okx.rs

# 修复Kraken
sed -i '/let crypto_price = CryptoPrice {/,/};/c\
                                let crypto_price = CryptoPrice::new(\
                                    symbol.to_string(),\
                                    price,\
                                    change_percent,\
                                    volume,\
                                    "Kraken".to_string(),\
                                );' src/exchanges/kraken.rs

echo "所有交易所文件已修复"
