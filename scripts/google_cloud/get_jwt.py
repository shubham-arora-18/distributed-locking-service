import logging

from create_jwt_from_sa import generate_jwt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


sa_keyfile = "/Users/shubhamarora/Downloads/distributed-locking-jwt.json"
sa_email = "jwt-sa@prefab-sky-412817.iam.gserviceaccount.com"
expire = 3000  # expire after secs
aud = "cloud-endpoint-proxy-application-z4ndkzhdma-uc.a.run.app"

jwt = generate_jwt(sa_keyfile, sa_email, expire, aud)

logger.info(f"\n\nJwt token = Bearer {jwt}\n\n")
