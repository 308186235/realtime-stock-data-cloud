#!/bin/bash
# Google Cloud VM 创建脚本

# 设置项目ID (替换为您的项目ID)
PROJECT_ID="your-trading-project"
INSTANCE_NAME="trading-backend"
ZONE="asia-east1-b"  # 台湾区域，延迟最低

# 创建VM实例
gcloud compute instances create $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --network-interface=network-tier=PREMIUM,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=default \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --create-disk=auto-delete=yes,boot=yes,device-name=$INSTANCE_NAME,image=projects/ubuntu-os-cloud/global/images/ubuntu-2004-focal-v20231213,mode=rw,size=30,type=projects/$PROJECT_ID/zones/$ZONE/diskTypes/pd-standard \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=env=production,app=trading \
    --reservation-affinity=any

# 创建防火墙规则允许HTTP/HTTPS流量
gcloud compute firewall-rules create allow-trading-api \
    --project=$PROJECT_ID \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:8000,tcp:80,tcp:443 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=trading-backend

# 为实例添加网络标签
gcloud compute instances add-tags $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --tags=trading-backend

echo "VM实例创建完成！"
echo "使用以下命令连接到实例："
echo "gcloud compute ssh $INSTANCE_NAME --project=$PROJECT_ID --zone=$ZONE"
