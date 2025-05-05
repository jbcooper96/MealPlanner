import scrapy
from bs4 import BeautifulSoup
from allrecipes.items import RecipeItem

class RecipeSpider(scrapy.Spider):
    name = "recipes"
    allowed_domains = ["allrecipes.com"]
    
    def start_requests(self):
        yield scrapy.Request(
            url='https://www.allrecipes.com/recipes-a-z-6735880',
            callback=self.parse,
            meta={'cookiejar': 1}
        )

    def get_csfr_token(self, response):
        set_cookie_headers = response.headers.getlist('Set-Cookie')
        for cookie in set_cookie_headers:
            cookie_text = cookie.decode()
            if "CSRFToken" in cookie_text:
                return cookie_text.split(';')[0].split('=')[1]
        return None


    def parse(self, response, tags=[]):
        soup = BeautifulSoup(response.text, "html.parser")
        new_token = self.get_csfr_token(response)
        if new_token:
            self.token = new_token
        if "/recipe" in response.url and "/recipes" not in response.url:
            self.logger.info("Found recipe")
            if self.token:
                self.logger.info("Found token")
                request = scrapy.Request(
                    response.url + "?print",
                    callback=self.parse_recipe,
                    cb_kwargs=dict(),
                )
                yield scrapy.FormRequest(
                    method="POST",
                    url=response.url + "?print",
                    formdata={"print": "true", "CSRFToken": self.token},
                    callback=self.parse_recipe,
                    cb_kwargs={"tags": tags},
                    meta={'cookiejar': response.meta['cookiejar']}
                )
            else:
                self.logger.info("Cant get token")
                self.logger.info(response.headers.getlist('Set-Cookie'))
        else:
            for link in soup.select("a"):
                link_tags = [tag for tag in tags]
                link_url = link["href"]
                if "/recipe" in link_url:
                    request = scrapy.Request(
                        link_url,
                        callback=self.parse,
                        cb_kwargs=dict(),
                        meta={'cookiejar': response.meta['cookiejar']}
                    )
                    
                    card_content = link.select_one("div.card__content", recursive=True)
                    
                    if card_content and card_content["data-tag"]:
                        link_tags.append(card_content["data-tag"])

                    if link.__class__ == "mntl-link-list__link text-body-100 global-link text-body-100 global-link":
                        link_tags.append(link.get_text(strip=True))


                    request.cb_kwargs["tags"] = link_tags
                    self.logger.info(link_tags)
                    yield request



    def parse_recipe(self, response, tags=[]):
        print("RECIPE")
        soup = BeautifulSoup(response.text, "html.parser")
        item = RecipeItem()
        item["title"] = soup.find("h1").get_text(strip=True)
        ingredients = []
        for li in soup.select("li.mm-recipes-structured-ingredients__list-item"):
            ingredientFields = dict()
            quantity = li.find("span", {"data-ingredient-quantity": "true"}, recursive=True)
            if quantity:
                ingredientFields["quantity"] = quantity.get_text(strip=True)

            unit = li.find("span", {"data-ingredient-unit": "true"}, recursive=True)
            if unit:
                ingredientFields["unit"] = unit.get_text(strip=True)

            ingredient = li.find("span", {"data-ingredient-name": "true"}, recursive=True)
            if ingredient:
                ingredientFields["ingredient"] = ingredient.get_text(strip=True)
            ingredients.append(ingredientFields)

        item["ingredients"] = ingredients
        item["instructions"] = " ".join(p.get_text(strip=True) for p in soup.select("#mm-recipes-steps_1-0 p"))
        item["nutritionFacts"] = soup.select_one("div.mm-recipes-nutrition-facts-label__contents").get_text(strip=True)
        item["tags"] = tags
        print("item")
        print(item)
        return item         
                    