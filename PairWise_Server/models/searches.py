from django.db import models
from PairWise_Server.models.users import User
from PairWise_Server.models.courses import CourseOffering, CourseSection
from PairWise_Server.models.data_tags import SkillTag, LocationTag


class SearchEntry(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(CourseOffering, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    size = models.PositiveSmallIntegerField(default=1)
    capacity = models.PositiveSmallIntegerField(default=2)
    required_section = models.ForeignKey(CourseSection, on_delete=models.SET_NULL, null=True)
    quality_cutoff = models.PositiveSmallIntegerField(default=0)
    active_search = models.BooleanField(default=True)


class AvailableSearchEntry(SearchEntry):
    pass


class AbandonedSearchEntry(SearchEntry):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class UserSearchData(models.Model):
    id = models.AutoField(primary_key=True)
    search = models.ForeignKey(SearchEntry, related_name='members', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_section = models.ForeignKey(CourseSection, on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(LocationTag, on_delete=models.CASCADE, null=True)
    desired_skills = models.ManyToManyField(SkillTag)


class SearchResultsCache(models.Model):
    searcher = models.ForeignKey(SearchEntry, on_delete=models.CASCADE)
    result = models.ForeignKey(SearchEntry, related_name='found', on_delete=models.CASCADE)
    match_coefficient = models.PositiveSmallIntegerField()
