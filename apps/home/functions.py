# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEYS

blogIdea = ''
keywords = ''


def generatedBlogTopicIdeas(blogIdea, audience, keywords):
    blog_topics = []
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Generate blog topics ideas on the given topic: {}\nAudience: {}\nkeywords: {}\n*".format(blogIdea,
                                                                                                         audience,
                                                                                                         keywords),
        temperature=0.8,
        max_tokens=250,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1)
    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
        else:
            return []
    else:
        return []

    a_list = res.split('*')

    if len(a_list) > 0:
        for blog in a_list:
            blog_topics.append(blog)
            # print(response)
            # print('My target Text ' + res)
            # print('My target a_list ' + blog)
            # print("The size of blog_topics \n")
            # print(len(blog_topics))

    return blog_topics


def generatedBlogSections(topic, keywords):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Generate blog topics ideas on the following topic:{}. \n \n   ".format(topic, keywords),
        temperature=0.8,
        max_tokens=1800,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1)
    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
        else:
            res = None
    else:
        res = None
    return res


def generatedBlogSectionTitles(blogIdea, audience, keywords):
    blog_Sections = []
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Generate blog titles for the given blog topic, audience and keywords Topic: {}\nAudience: {"
               "}\nkeywords: {}\n*".format(blogIdea, audience, keywords),

        temperature=0.8,
        max_tokens=250,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1)
    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
        else:
            return []
    else:
        return []

    a_list = res.split('*')

    if len(a_list) > 0:
        for blog in a_list:
            blog_Sections.append(blog)
            # print(response)
            # print('My target Text ' + res)
            # print('My target a_list ' + blog)
            # print("The size of blog_topics \n")
            # print(len(blog_topics))

    return blog_Sections


# res = generatedBlogTopicIdeas(topic, keywords)[0].replace('/n', '')
# b_list = res[0].split('*')
# for blog in b_list:
#     blog_topics.append(blog)
#     print('\n')
#     print(blog)

def generatedBlogSectionDetails(blogTopic, SectionTopic, audience, keywords):
    blog_Sections = []
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Generate detailed section write up for the following blog section/"
               " heading, using the blog title, audience and keywords provided./"
               "\nBlog Title: {}\nBlog Section Heading: {}\nAudience: /"
               "{}\nKeywords: {}\n\n".format(blogTopic, SectionTopic, audience, keywords),

        temperature=0.8,
        max_tokens=500,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1)
    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
            cleanedRes = res.replace('\n', '<br>')
            return cleanedRes
        else:
            return []
    else:
        return []

    a_list = res.split('*')

    if len(a_list) > 0:
        for blog in a_list:
            blog_Sections.append(blog)
            # print(response)
            # print('My target Text ' + res)
            # print('My target a_list ' + blog)
            # print("The size of blog_topics \n")
            # print(len(blog_topics))

    return blog_Sections

def checkCountAllowance(profile):
    if profile.subscribed:
        ## User has a subscription
        type = profile.subscriptionType
        if type == 'free':
            max_limit = 5000
            if profile.monthlyCount:
                if int(profile.monthlyCount) < max_limit:
                    return True
                else:
                    return False
            else:
                return True

        elif type == 'starter':
            max_limit = 40000
            if profile.monthlyCount:
                if int(profile.monthlyCount) < max_limit:
                    return True
                else:
                    return False
            else:
                return True
        elif type == 'advanced':
            return True
        else:
            return False
    else:
        max_limit = 5000
        if profile.monthlyCount:
            if int(profile.monthlyCount) < max_limit:
                return True
            else:
                return False
        else:
            return True





    monthlyCount
    subscribed
    subscriptionType
