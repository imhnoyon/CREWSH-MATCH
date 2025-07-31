from rest_framework import serializers

from .models import (
    Text,
    Photo,
    File
)


MAX_FILESIZE = {
    "photo": 2,
    "file": 10
}


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = ("id", "text")


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ("id", "photo")

    def validate_photo(self, value):
        if value.size > MAX_FILESIZE["photo"] * 1024 * 1024:
            raise serializers.ValidationError({
                    "content_data": "Image file must not be greater than %s mb" % MAX_FILESIZE["photo"]
                })
        return value


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("id", "file")

    def validate_file(self, value):
        if value.size > MAX_FILESIZE["file"] * 1024 * 1024:
            raise serializers.ValidationError({
                    "content_data": "File must not be greater than %s mb" % MAX_FILESIZE["file"]
                })
        return value


CONTENT_TYPE_MAP = {
    'text': (Text, TextSerializer),
    'photo': (Photo, PhotoSerializer),
    "file": (File, FileSerializer)
}


class DynamicContentSerializer(serializers.Serializer):
    content_type_key = serializers.ChoiceField(choices=["text", "file", "photo"])
    content_data = serializers.SerializerMethodField()

    def get_fields(self):
        # This overrides the fields dynamically after `content_type_key` is available
        fields = super().get_fields()
        content_type_key = self.initial_data.get("content_type_key")

        if content_type_key == "text":
            fields['content_data'] = serializers.CharField()
        elif content_type_key in ["file", "photo"]:
            fields['content_data'] = serializers.FileField()
        else:
            fields['content_data'] = serializers.CharField(required=False)

        return fields

    def validate(self, attrs):
        content_type_key = attrs.get("content_type_key")
        content_data = attrs.get("content_data")

        if content_type_key not in CONTENT_TYPE_MAP:
            raise serializers.ValidationError("Unsupported content type")
            
        # Wrap content_data into the field expected by the inner serializer
        inner_field_name = content_type_key
        inner_serializer_cls = CONTENT_TYPE_MAP[content_type_key][1]
        inner_serializer = inner_serializer_cls(data={inner_field_name: content_data})
        inner_serializer.is_valid(raise_exception=True)

        # Save for later use in create()
        self._validated_content_obj = inner_serializer.save()
        return attrs
    
    def save(self, **kwargs):
        return self._validated_content_obj
    

class DynamicMultipleContentSerializer(serializers.Serializer):
    content_type_key = serializers.ChoiceField(choices=["file", "photo"])
    content_data = serializers.ListField(child=serializers.FileField())

    def validate(self, attrs):
        content_type_key = attrs.get("content_type_key")
        content_data = attrs.get("content_data")

        if content_type_key not in CONTENT_TYPE_MAP:
            raise serializers.ValidationError("Unsupported content type")
            
        # Wrap content_data into the field expected by the inner serializer
        self._validated_content_obj = []

        for f in content_data:
            inner_field_name = content_type_key
            inner_serializer_cls = CONTENT_TYPE_MAP[content_type_key][1]
            inner_serializer = inner_serializer_cls(data={inner_field_name: f})
            inner_serializer.is_valid(raise_exception=True)

            # Save for later use in create()
            self._validated_content_obj.append(inner_serializer.save())
            
        return attrs
    
    def save(self, **kwargs):
        return self._validated_content_obj
    
