import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional


class ImageStorage:
    """
    Handles image storage - either S3 or local filesystem.
    Automatically detects if AWS credentials are available.
    """

    def __init__(self):
        self.use_s3 = False
        self.s3_client = None
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.region = os.getenv("S3_REGION", "us-east-1")

        # Auto-detect RunPod URL from RUNPOD_POD_ID environment variable
        runpod_pod_id = os.getenv("RUNPOD_POD_ID")
        if runpod_pod_id:
            self.local_base_url = f"https://{runpod_pod_id}-8000.proxy.runpod.net"
            print(f"Auto-detected RunPod URL: {self.local_base_url}")
        else:
            # Fallback to PUBLIC_URL or localhost
            self.local_base_url = os.getenv("PUBLIC_URL", os.getenv("LOCAL_BASE_URL", "http://localhost:8000"))
            print(f"Using base URL: {self.local_base_url}")

        # Try to initialize S3
        self._init_s3()

    def _init_s3(self):
        """Initialize S3 client if credentials are available"""
        try:
            aws_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")

            if aws_key and aws_secret and self.bucket_name:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_key,
                    aws_secret_access_key=aws_secret,
                    region_name=self.region
                )

                # Test connection
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                self.use_s3 = True
                print(f"S3 storage initialized: {self.bucket_name}")

            else:
                print("S3 credentials not found, using local storage")

        except ClientError as e:
            print(f"S3 initialization failed: {e}")
            print("Falling back to local storage")
            self.use_s3 = False

    def upload(self, local_path: str, image_id: str) -> str:
        """
        Upload image to S3 or return local URL.

        Args:
            local_path: Path to local image file
            image_id: Unique identifier for the image

        Returns:
            Public URL to the image
        """

        filename = f"{image_id}.png"

        if self.use_s3:
            try:
                # Upload to S3
                self.s3_client.upload_file(
                    local_path,
                    self.bucket_name,
                    filename,
                    ExtraArgs={
                        'ContentType': 'image/png',
                        'ACL': 'public-read'
                    }
                )

                # Generate S3 URL
                url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"
                print(f"Uploaded to S3: {url}")
                return url

            except ClientError as e:
                print(f"S3 upload failed: {e}")
                print("Falling back to local URL")

        # Return local URL
        url = f"{self.local_base_url}/images/{filename}"
        print(f"Using local URL: {url}")
        return url

    def delete(self, image_id: str) -> bool:
        """
        Delete image from storage.

        Args:
            image_id: Unique identifier for the image

        Returns:
            True if successful
        """

        filename = f"{image_id}.png"

        if self.use_s3:
            try:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=filename
                )
                print(f"Deleted from S3: {filename}")
                return True

            except ClientError as e:
                print(f"S3 delete failed: {e}")

        # Delete local file
        local_path = f"/app/generated_images/{filename}"
        if os.path.exists(local_path):
            os.remove(local_path)
            print(f"Deleted local file: {filename}")
            return True

        return False

    def get_url(self, image_id: str) -> str:
        """
        Get URL for an image.

        Args:
            image_id: Unique identifier for the image

        Returns:
            URL to the image
        """

        filename = f"{image_id}.png"

        if self.use_s3:
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"
        else:
            return f"{self.local_base_url}/images/{filename}"
