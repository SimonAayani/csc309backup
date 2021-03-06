from rest_framework import serializers
from PairWise_Server.models import DataTag, Course, Profile, User, Notification, CourseOffering, Term,\
                                   UserSearchData, CourseSection, AvailableSearchEntry, SearchResultsCache


class DataTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataTag
        fields = ('id', 'tag_text')


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('course_id', 'course_code', 'name')


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ('year', 'term')


class CourseOfferingSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='course_code', read_only=True)
    term = TermSerializer(read_only=True)

    class Meta:
        model = CourseOffering
        fields = ('course', 'term')


class CourseSectionSerializer(serializers.ModelSerializer):
    offering = CourseOfferingSerializer(read_only=True)

    class Meta:
        model = CourseSection
        fields = ('section_id', 'section_name', 'offering')


class ProfilePicSerializer(serializers.ModelSerializer):
    pic = serializers.ImageField(max_length=100, read_only=True)

    class Meta:
        model = Profile
        fields = ('pic',)


class ProfilePicMapSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(slug_field='username', read_only=True)
    pic = serializers.ImageField(max_length=100, read_only=True)

    class Meta:
        model = Profile
        fields = ('student', 'pic')


class UserSerializer(serializers.ModelSerializer):
    profile_set = ProfilePicSerializer(many=True, allow_null=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'profile_set', 'last_login', 'date_joined')


class ProfileReadSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    courses = CourseSerializer(many=True, read_only=True)
    location = DataTagSerializer(read_only=True)
    skills = DataTagSerializer(many=True, read_only=True)
    pic = serializers.ImageField(max_length=100, read_only=True)

    class Meta:
        model = Profile
        fields = ('student', 'courses', 'location', 'skills', 'bio', 'pic')


class ProfileWriteSerializer(serializers.ModelSerializer):
    pic = serializers.ImageField(max_length=100, allow_null=True)

    class Meta:
        model = Profile
        fields = ('student', 'courses', 'location', 'skills', 'bio', 'pic')


class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(slug_field='username', read_only=True)
    receiver = serializers.SlugRelatedField(slug_field='username', read_only=True)
    category = CourseOfferingSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'sender', 'receiver', 'category')


class UserSearchDataSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    course_section = CourseSectionSerializer(read_only=True)
    location = DataTagSerializer(read_only=True)
    desired_skills = DataTagSerializer(many=True, read_only=True)

    class Meta:
        model = UserSearchData
        fields = ('id', 'user', 'course_section', 'location', 'desired_skills')


class SearchEntrySerializer(serializers.ModelSerializer):
    category = CourseOfferingSerializer(read_only=True)
    required_section = CourseSectionSerializer(read_only=True)
    members = UserSearchDataSerializer(many=True, read_only=True)

    class Meta:
        model = AvailableSearchEntry
        fields = ('id', 'category', 'title', 'description', 'size', 'capacity', 'required_section', 'members')


class ResultsCacheSerializer(serializers.ModelSerializer):
    result = SearchEntrySerializer(read_only=True)

    class Meta:
        model = SearchResultsCache
        fields = ('result', 'match_coefficient')
