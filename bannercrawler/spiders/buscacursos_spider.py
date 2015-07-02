#!/usr/local/bin python
# -*- encoding: utf-8 -*-
import scrapy
from bannercrawler.items import Curso
from collections import defaultdict


class BuscacursosSpider(scrapy.Spider):
    name = "buscacursos"
    start_urls = ["http://www3.uc.cl/buscacursos/"]

    # Selectores
    # TODO: Optimizar selectores
    campus_selector = "form[name='cxml_buscador_form'] " + \
            "select[name='cxml_campus'] option"
    course_selector = "div.centro > div > table tr[class^='resultadosRow']"
    semester = "2015-2"

    def parse(self, resp):
        options = resp.css(self.campus_selector)
        options.pop(0)

        for campus in options:
            yield scrapy.FormRequest(
                    # TODO: Averiguar si hay alguna forma mejor de hacer esto
                    # con scrapy.
                    url=self.start_urls[0] + \
                            "?cxml_semestre={}&cxml_campus={}".format(
                                self.semester,
                                str(campus.xpath("@value").extract()[0])
                                ),
                    callback=self.parse_each_campus_page
            )

    def parse_each_campus_page(self, resp):
        courses = resp.css(self.course_selector)

        for course in courses:
            yield self.parse_each_course(course)

    def parse_each_course(self, courseElement):
        tds = courseElement.xpath("td") 

        # NRC
        nrc = int(tds[0].xpath("text()").extract()[0])

        # Nombre
        name = tds[1].xpath("@title").extract()[0].encode("utf-8")

        # Seccion
        section = tds[4].xpath("text()").extract()[0].encode("utf-8")

        # Profesor
        try:
            teacher = tds[8].css("a::text").extract()[0].encode("utf-8")
        except IndexError:
            teacher = "Sin profesores"

        # Creditos
        credits = tds[10].xpath("text()").extract()[0].encode("utf-8")

        # Horario, la parte más *compleja*
        schedule = self.parse_schedule(tds[6])

        # Crear el curso...
        course = Curso()
        course["nrc"] = nrc
        course["nombre"] = name
        course["seccion"] = section
        course["profesor"] = teacher
        course["creditos"] = credits
        course["horarios"] = schedule

        return course


    def parse_schedule(self, data):
        trs = data.css("tr")
        schedule = defaultdict(list)

        for tr in trs:
            tds = tr.xpath("td")
            type_ = tds[1].xpath("text()").extract()[0].encode("utf-8")
            days, modules = (tds[0].xpath("text()").extract()[0]
                    .encode("utf-8").split(":"))
            days = days.split("-")
            modules = modules.split(",")

            merged = []

            for day in days:
                merged += list(map(
                    lambda m: day + m,
                    modules
                ))

            schedule[type_] += merged

        return schedule
