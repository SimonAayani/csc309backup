from PairWise_Server.models import AvailableSearchEntry, AbandonedSearchEntry, UserSearchData, SearchResultsCache, CourseOffering, Course
from django.contrib.auth.models import User
from django.db.models import Count, Q, F
from PairWise_Server.fetch import fetch_user_by_username, fetch_term_by_time_of_year,\
                                  fetch_offering_by_term, fetch_course_by_course_code


def cancel_search(user, offering):
    AvailableSearchEntry.objects.filter(members__user=user, category=offering).delete()


def mark_search_result(searcher, found, match_coefficient):
    SearchResultsCache.objects.create(searcher=searcher, result=found, match_coefficient=match_coefficient)


def get_marked_results(searcher, category=None):
    if category is None:
        return list(SearchResultsCache.objects.filter(searcher__members__user=searcher))
    else:
        return list(SearchResultsCache.objects.filter(searcher__members__user=searcher,
                                                      searcher__category=category))


def abandon_search(user_search_data):
    search_entry = user_search_data.search
    SearchResultsCache.objects.filter(Q(searcher=search_entry) | Q(result=search_entry)).delete()
    new_abandoned = AbandonedSearchEntry.objects.create(category=search_entry.category,
                                                        title=search_entry.title,
                                                        description=search_entry.description,
                                                        size=search_entry.size,
                                                        capacity=search_entry.capacity,
                                                        required_section=search_entry.required_section,
                                                        quality_cutoff=search_entry.quality_cutoff,
                                                        active_search=search_entry.active_search,
                                                        owner=user_search_data.user)
    new_abandoned.save()
    search_entry.delete()


def recover_search(user, category):
    abandoned_search = AbandonedSearchEntry.objects.get(owner=user, category=category)
    recovered_search = AvailableSearchEntry.objects.create(category=abandoned_search.category,
                                                           title=abandoned_search.title,
                                                           description=abandoned_search.description,
                                                           size=abandoned_search.size,
                                                           capacity=abandoned_search.capacity,
                                                           required_section=abandoned_search.required_section,
                                                           quality_cutoff=abandoned_search.quality_cutoff,
                                                           active_search=abandoned_search.active_search)
    recovered_search.save()

    search_criteria = UserSearchData.objects.get(user=user, course_section__offering=category)
    search_criteria.search = recovered_search
    search_criteria.save()

    update_cache(recovered_search)
    abandoned_search.delete()


def measure_matches(search_entry):
    skill_reqs = []
    locations = []
    sections = []
    for user_search in search_entry.members.all():
        skill_reqs.extend(list(user_search.user.profile_set.all()[0].skills.all()))
        locations.append(user_search.location)
        sections.append(user_search.course_section)

    condition = Q(required_section=sections[0])
    if len(sections) > 1:
        for section in sections[1:]:
            condition &= Q(required_section=section)

    category = search_entry.category
    my_match_filter = Q(members__user__profile__skills__in=skill_reqs)
    other_match_filter = Q(members__desired_skills__in=skill_reqs)
    my_size = search_entry.size

    if search_entry.required_section is None:
        targets = AvailableSearchEntry.objects.filter(category=category, size__lte=(F('capacity') - my_size))\
                                              .exclude(Q(id=search_entry.id) | (Q(required_section__isnull=False) & ~condition))
    else:
        targets = AvailableSearchEntry.objects.filter(category=category, size__lte=(F('capacity') - my_size))\
                                              .exclude(Q(id=search_entry.id) | ~Q(members__course_section=search_entry.required_section)
                                                       | (Q(required_section__isnull=False) & ~condition))

    # Additional conditions: Section, location
    results = targets.annotate(my_match_coeff=(Count('members__user__profile__skills', filter=my_match_filter)),
                               other_match_coeff=Count('members__desired_skills', filter=other_match_filter),
                               location_bonus=Count('members__location', filter=Q(members__location__in=locations)),
                               section_bonus=Count('members__course_section', filter=Q(members__course_section__in=sections)))
    print(results)
    matches = results.annotate(abs_match_coeff=(F('my_match_coeff') * 60 + F('other_match_coeff') * 15 +
                                                F('section_bonus') * 15 + F('location_bonus') * 5)
                               ).filter(abs_match_coeff__gte=search_entry.quality_cutoff).order_by('-abs_match_coeff')

    for match in matches:
        mark_search_result(search_entry, match, match.abs_match_coeff)


def update_cache(search_entry):
    SearchResultsCache.objects.filter(Q(searcher=search_entry) | Q(result=search_entry)).delete()
    measure_matches(search_entry)

    skill_reqs = []
    locations = []
    sections = []
    for user_search in search_entry.members.all():
        skill_reqs.extend(list(user_search.user.profile_set.all()[0].skills.all()))
        locations.append(user_search.location)
        sections.append(user_search.course_section)

    category = search_entry.category
    my_match_filter = Q(members__user__profile__skills__in=skill_reqs)
    other_match_filter = Q(members__desired_skills__in=skill_reqs)
    my_size = search_entry.size

    condition = Q(required_section=sections[0])

    if len(sections) > 1:
        for section in sections[1:]:
            condition &= Q(required_section=section)

    if search_entry.required_section is None:
        targets = AvailableSearchEntry.objects.filter(category=category, size__lte=(F('capacity') - my_size))\
                                              .exclude(Q(id=search_entry.id) | (Q(required_section__isnull=False) & ~condition))
    else:
        targets = AvailableSearchEntry.objects.filter(category=category, size__lte=(F('capacity') - my_size))\
                                              .exclude(Q(id=search_entry.id) | ~Q(members__course_section=search_entry.required_section)
                                                       | (Q(required_section__isnull=False) & ~condition))

    results = targets.annotate(my_match_coeff=(Count('members__user__profile__skills', filter=my_match_filter)),
                               other_match_coeff=Count('members__desired_skills', filter=other_match_filter),
                               location_bonus=Count('members__location', filter=Q(members__location__in=locations)),
                               section_bonus=Count('members__course_section', filter=Q(members__course_section__in=sections)))
    print(results)
    matches = results.annotate(abs_match_coeff=(F('my_match_coeff') * 15 + F('other_match_coeff') * 60 +
                                                F('section_bonus') * 15 + F('location_bonus') * 5)
                               ).filter(abs_match_coeff__gte=search_entry.quality_cutoff).order_by('-abs_match_coeff')

    for match in matches:
        mark_search_result(match, search_entry, match.abs_match_coeff)
