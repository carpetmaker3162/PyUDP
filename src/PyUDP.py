from bs4 import BeautifulSoup
import requests
import re
import json
from fuzzywuzzy import fuzz
from difflib import get_close_matches
from string import digits

_digits = digits + "."

__all__ = [
    "Unit",
    "BaseUnit",
]

with open("src/all_units.json", "r") as file:
    ALL_UNITS = json.loads(file.read())
    file.close()

with open("src/tf_items.json", "r") as file:
    ALL_MATERIALS = json.loads(file.read())
    file.close()

def _search(substring):
    with open("src/all_units.json", "r") as file:
        s = json.loads(file.read())
        file.close()
    if substring.lower() in [x.lower() for x in s.values()]:
        return list(s.values())[[x.lower() for x in s.values()].index(substring.lower())]
    for i in s.values():
        if fuzz.partial_ratio(i.lower(), substring) == 100 and len(substring) > 4:
            return i
    else:
        if get_close_matches(substring, s.values(), cutoff=0.5):
            return get_close_matches(substring, s.values(), cutoff=0.5)
        else:
            return None

def _get_pid(name):
    try:
        return int(list(ALL_UNITS.keys())[list(ALL_UNITS.values()).index(name)])
    except ValueError:
        return None

def _update_unit_data(_upper_bound_UID: int):
    s = {}
    for i in range(_upper_bound_UID):
        r = requests.get(f"https://thanksfeanor.pythonanywhere.com/UDP/{i}")
        if r.status_code == 500:
            raise Exception(f"Unit with ID {i} not found")
        soup = BeautifulSoup(r.text, 'html.parser')
        unitname = re.sub('<.*?>', '', str(soup.find('title'))).replace('UDP', '').strip()
        print(f"{i}: {unitname}")
        s[i] = str(unitname)

def get_number(string):
    return float("".join(list(filter(lambda a: a in _digits, string))))

class BaseUnit:
    """
    Basically a "shell" version of `Unit` (contains only the most basic attributes like ID and name).
    Exclusively for getting unit UIDs/names (since using `Unit` for that purpose is much slower)
    """
    def __init__(self, name: str = None, UID: int = None) -> None:
        if UID != None:
            self.id = UID
            self.name = ALL_UNITS[str(self.id)]
        elif name == None and UID == None:
            raise Exception("Please provide a name, or the Unit ID if you have it already")
        else:
            if name:
                _name = _search(name)
                if isinstance(_name, list):
                    raise Exception(f"Several possible matches found. Did you mean:\n{chr(10).join(_name)}")
                else:
                    self.id = _get_pid(_name)
                    self.name = _name
    
    def __repr__(self):
        return f"<BaseUnit object ({self.id} {self.name})>"
    
    def __str__(self):
        return f"{self.name} (UID: {self.id})"

class Unit(BaseUnit):
    def __init__(self, name: str = None, UID: int = None) -> None:
        super().__init__(name, UID)
        
        self._r = requests.get(f"https://thanksfeanor.pythonanywhere.com/UDP/{self.id}")
        self._soup = BeautifulSoup(self._r.text, "html.parser")

        self.description = [x.text for x in self._soup.find("div", {"class": "collapse show"}).find_all("p") if "To propose corrections" not in x.text and x.text.strip()]
        
        self.xp_curve = self._get_xp_curve()
        self.xp_curve[1] = 0

    def _get_xp_curve(self):
        xp_curve = {}
        for i in self._soup.find_all("tr"):
            for idx, j in enumerate(i.find_all("td")):
                if j.text.endswith("XP") and "-" not in i.find_all("td")[idx-1].text:
                    xp_curve[int(i.find_all("td")[idx-1].text)] = get_number(j.text)
        return xp_curve
    
    def upgrade(self, bound: int, upper_bound: int = None):
        """
        Get the amount of xp required to upgrade the unit from level `bound` to level `upper_bound`.
        If `upper_bound` is not provided, function will return the xp required to upgrade the unit 
        from level 0 to level `bound`.
        ## Examples:
        
        # XP required to upgrade Jizo from Lv10 to Lv20
        >>> Unit("Kasa Jizo").upgrade(10, 20)
        2166200

        # XP required to upgrade hip hop cat (Can Can) to Lv30
        >>> Unit("hip hop").upgrade(30)
        4285850
        """
        
        if not upper_bound:
            upper_bound = bound
            bound = 1
        total = 0
        for i in range(bound + 1, upper_bound + 1):
            try:
                total += self.xp_curve[i]
            except KeyError as e:
                raise Exception(f"Invalid level (check whether {self.name} can really be upgraded to level {upper_bound} from level {bound})")
        return int(total)
    
    @property
    def catcombos(self):
        """
        Returns a `dict` with all CatCombos containing the unit.
        ## Examples:

        >>> Unit("lasvoss").catcombos
        {'Bad Guys - Research Power UP (L)': ['519', '172', '319']}
        """
        unit_combos = {}
        for sub in str(self._soup.find("div", {"id" : "combocollapse"})).split("<br/>\n<br/>"):
            newsoup = BeautifulSoup(sub, 'html.parser')
            if newsoup.text.strip():
                unit_combos[newsoup.text.strip()] = []
            else:
                continue
            for link in newsoup.find_all("a"):
                unit_combos[newsoup.text.strip()].append(link.get("href").replace("\\UDP\\", ""))
        return unit_combos
    
    @property
    def tf_requirements(self):
        """
        Returns a `dict` containing true form requirements.
        If the unit doesn't have one, it will return an empty dict.
        ## Examples:

        >>> Unit("lasvoss").tf_requirements
        {'XP': '1000000', 'EPIC_CATFRUIT_SEED': '10', 'ELDER_CATFRUIT': '1', 'GOLD_CATFRUIT': '1'}

        >>> Unit("baby gao").tf_requirements
        {}
        """
        _tf_requirements = {}
        try:
            trs = self._soup.find("table", {"class" : "table table-bordered border-4 border-success"}).find_all("tr")
        except AttributeError as e:
            return _tf_requirements
        for i, q in zip(trs[0], trs[1]):
            if not isinstance(i.find("img"), int) and q.text.strip():
                item = re.search(r"_(\d+)_f", i.find("img").get("src"), flags=0).group(1)
                quantity = q.text.strip().removeprefix("×")
                _tf_requirements[ALL_MATERIALS[item]] = quantity
        return _tf_requirements
    
    @property
    def talents(self):
        """
        Returns a `dict` containing the unit's talents as keys and their priorities as values.
        ## Examples:

        >>> Unit("hip hop").talents
        {'Money Up': 10.0, 'Target Alien': 6.79, 'Defense Buff': 3.26, 'Attack Buff': 5.02, 'Move Speed Up': 8.71}
        
        >>> Unit("kasli the bane").talents
        {}

        >>> why doesnt dasli have talents
        because shes broken already
        """
        _talents = {}
        try:
            for i in self._soup.find("div", {"id": "talentcollapse"}).find_all("tr"):
                if not i.find_all("td"):
                    continue
                tri = [td.text for td in i.find_all("td") if "priority" not in td.text.lower()]
                _talents[tri[0]] = float(tri[1])
        except (ValueError, AttributeError) as e:
            pass
        return _talents