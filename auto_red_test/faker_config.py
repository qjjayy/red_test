#!/usr/bin/env python
# -*- coding:utf-8 -*-
import collections
faker_config = collections.OrderedDict(
    int=collections.OrderedDict(
        date_time_this_month=[
            'date', 'time'
        ]
    ),
    unicode=collections.OrderedDict(
        country_code=[
            'country_code'
        ],
        address=[
            'address', 'street'
        ],
        postcode=[
            'postcode'
        ],
        zipcode=[
            'zipcode'
        ],
        city=[
            'city'
        ],
        country=[
            'country'
        ],
        ean8=[
            'code', '_no', '_number'
        ],
        company=[
            'company'
        ],
        currency_code=[
            'currency'
        ],
        free_email=[
            'email'
        ],
        url=[
            'url', 'attachment', 'photo'
        ],
        job=[
            'job', 'role'
        ],
        name=[
            'name'
        ],
        phone_number=[
            'phone'
        ],
        uuid=[
            'uuid'
        ],
        object_id=[
            'id'
        ]
    )
)
