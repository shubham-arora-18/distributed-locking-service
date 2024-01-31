import logging

from create_jwt_from_sa import generate_jwt

# to allow jwt authentication,
# 1. you create a service account named jwt-sa for example and download the json key for it.
# 2. Then based on service account name, you configure your endpoint-service-definition.yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


sa_keyfile = "/Users/shubhamarora/Downloads/key.json"
sa_email = "jwt-sa@prefab-sky-412817.iam.gserviceaccount.com"
expire = 3000  # expire after secs
aud = "cloud-endpoint-proxy-application-z4ndkzhdma-uc.a.run.app"

jwt = generate_jwt(sa_keyfile, sa_email, expire, aud)

logger.info(f"\n\nJwt token = Bearer {jwt}\n\n")
