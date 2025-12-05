import json

from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import  Profile, Image

User = get_user_model()


EMAIL_SUBJECTS = {
    "account_verification": "Verify Account for Crew Match",
    "rest_password": "Reset Password for Crew Match"
}

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    user_id = serializers.IntegerField(source='id', read_only=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "user_id", "full_name", "email_address", "password", "password2", "photo",
            "is_active", "is_subscribed", "is_private", "role",
            "created_at",
        )
        read_only_fields = ("is_active", )

    def validate_email_address(self, value):
        user_exists = User.objects.filter(email_address=value, is_active=True, is_verified=True)
        if user_exists:
            raise serializers.ValidationError("User with the following email_address already exists")
        return value

    def validate_password2(self, value):
        password = self.initial_data.get("password")

        if password and value and password != value:
            raise serializers.ValidationError("Passwords mismatched.")

        return value

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create(
            is_active=False,
            **validated_data
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['photo'] = instance.get_photo()
        profile = instance.get_profile()
        response['profile'] = profile
        response['images'] = ImageSerializer(instance.images.all(), many=True).data
        if profile:
            response['profile'] = ProfileSerializer(profile).data
            response['profile'].pop("user")
        return response


class S(serializers.ModelSerializer):
    def validate(self, attrs):
        super().validate(attrs)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ["id", "user", ]

    def to_representation(self, instance):
        context = super().to_representation(instance)
        user = instance.user
        ship = instance.ship
        company = instance.company
        context['user'] = {"full_name": user.full_name}
        context['company'] = {"id": company.id, "name": company.name}
        context['ship'] = {"id": ship.id, "name": ship.name}
        return context


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(method_name="get_photo", read_only=True)

    class Meta:
        model = Image
        fields = ("id", "user", "image", )

    def get_photo(self, obj):
        # request = self.context.get("request")
        # if obj.image and hasattr(obj.image, "url"):
        #     return obj.user.get_photo()
        # return None
        return obj.get_url()


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("image", )


class MultipleImageUploadSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.ImageField(), allow_empty=False)

    def validate_images(self, value):
        size_in_mb = 2
        max_size = size_in_mb * 1024 * 1024
        for image in value:
            if image.size > max_size:
                raise serializers.ValidationError(f"File must not exceed {size_in_mb} Mb")
        return value

    def create(self, validated_data):
        images = self.validated_data['images']
        request = self.context.get("request")

        image_objects = [ Image(user=request.user, image=image) for image in images]
        return Image.objects.bulk_create(image_objects)


class UpdateAndReplacePhotosSerializer(serializers.Serializer):
    new_images = serializers.ListField(child=serializers.ImageField(), allow_empty=True, required=False)
    replace = serializers.CharField(required=False)

    def validate(self, attrs):
        try:
            if attrs.get("replace"):
                replace_data = json.loads(attrs['replace'])
        except Exception as e:
            raise serializers.ValidationError({"message": str(e)})
        return attrs

    def validate_new_images(self, value):
        size_in_mb = 2
        max_size = size_in_mb * 1024 * 1024
        for image in value:
            if image.size > max_size:
                raise serializers.ValidationError(f"File must not exceed {size_in_mb} Mb")
        return value

    def save(self, **kwargs):
        replace_image_idx = json.loads(self.validated_data.get('replace', '{}'))
        new_images = self.validated_data.get('new_images', [])
        uploaded_images = []
        replaced_images = []
        request = self.context.get("request")

        for i, img in enumerate(new_images):
            if str(i) in replace_image_idx:
                replaced_images.append({"id": replace_image_idx.get(str(i)), "image": img})
            else:
                uploaded_images.append(img)

        for r in replaced_images:
            try:
                image = Image.objects.get(id=r['id'])
                image.image = r['image']
                image.save(update_fields=['image'])
            except Exception as e:
                print("Error updating %s" % str(e))

        image_objects = [Image(user=request.user, image=image) for image in uploaded_images]

        return Image.objects.bulk_create(image_objects)


class UpdatePhotosSerializer(serializers.Serializer):
    deleted_images = serializers.ListField(child=serializers.IntegerField(), allow_empty=True, required=False)
    new_images = serializers.ListField(child=serializers.ImageField(), allow_empty=True, required=False)

    def validate_new_images(self, value):
        size_in_mb = 2
        max_size = size_in_mb * 1024 * 1024
        for image in value:
            if image.size > max_size:
                raise serializers.ValidationError(f"File must not exceed {size_in_mb} Mb")
        return value

    def save(self, **kwargs):
        deleted_images = self.validated_data.get('deleted_images', [])
        new_images = self.validated_data.get('new_images', [])
        request = self.context.get("request")

        Image.objects.filter(id__in=deleted_images).delete()
        image_objects = [Image(user=request.user, image=image) for image in new_images]

        return Image.objects.bulk_create(image_objects)


class UserDetailsSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='id', read_only=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "user_id", "full_name", "email_address", "photo",
            "is_active", "is_subscribed", "is_private", "role",
            "created_at",
        )
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['photo'] = instance.get_photo()
        profile = instance.get_profile()

        response['images'] = [{"url": image.get_url()} for image in instance.images.all()]

        if profile:
            response['id'] = profile.id
            response["bio"] = profile.bio
            response["dob"] = profile.dob
            response["gender"] = profile.gender
            response["company"] = profile.company.name
            response["ship"] = profile.ship.name
            response["country"] = profile.country
            response["gender_preference"] = profile.gender_preference
            response['age'] = profile.age
            response['banned_countries'] = [country for country in profile.banned_countries]

        return response
