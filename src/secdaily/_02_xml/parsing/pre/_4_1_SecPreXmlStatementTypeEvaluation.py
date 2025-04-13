from dataclasses import dataclass
from typing import Dict, List

from secdaily._02_xml.parsing.pre._2_SecPreXmlTransformation import SecPreTransformLocationDetails


@dataclass
class EvalEntry:
    includes: List[str]
    excludes: List[str]
    confidence: int = 0


@dataclass
class StmtEvalDefinition:
    role_keys: List[EvalEntry]
    root_keys: List[EvalEntry]
    label_list: List[EvalEntry]


@dataclass
class StmtConfidence:
    byRole: int
    byRoot: int
    byLabel: int

    def get_max_confidenc(self):
        return max(self.byRole, self.byRoot, self.byLabel)

    def get_confidence_sum(self):
        return self.byLabel + self.byRole + self.byRoot


class SecPreXmlStatementTypeEvaluator:

    # confidence of 3 is max
    # # stmt
    #     role_keys: [{includes, excludes, confidence}]
    #     root_keys
    #     label_list -> evtll noch mit versionliste und tagliste unterscheiden

    stmt_eval_dict = {
        "CP": StmtEvalDefinition(
            role_keys=[
                EvalEntry(includes=["role/cover"], excludes=[], confidence=3),
                EvalEntry(includes=["coverpage"], excludes=[], confidence=3),
                EvalEntry(includes=["coverabstract"], excludes=[], confidence=3),
                EvalEntry(includes=["deidocument"], excludes=[], confidence=3),
                EvalEntry(includes=["document", "entity", "information"], excludes=[], confidence=3),
            ],
            root_keys=[
                EvalEntry(includes=["document", "entity", "information"], excludes=[], confidence=3),
                EvalEntry(includes=["coverpage"], excludes=[], confidence=3),
                EvalEntry(includes=["coverabstract"], excludes=[], confidence=3),
            ],
            label_list=[],
        ),
        "BS": StmtEvalDefinition(
            role_keys=[
                EvalEntry(
                    includes=["consolidated", "statement", "financialposition"], excludes=["detail"], confidence=3
                ),
                EvalEntry(
                    includes=["consolidated", "statement", "financialcondition"], excludes=["detail"], confidence=3
                ),
                EvalEntry(includes=["consolidated", "statement", "condition"], excludes=["detail"], confidence=3),
                EvalEntry(includes=["consolidated", "balance", "sheet"], excludes=["detail"], confidence=3),
                EvalEntry(includes=["consolidated", "financialposition"], excludes=["detail"], confidence=3),
                EvalEntry(includes=["condensed", "balance", "sheet"], excludes=["detail"], confidence=3),
                EvalEntry(includes=["statement", "balance", "sheet"], excludes=["detail"], confidence=3),
                EvalEntry(includes=["statement", "financialposition"], excludes=["detail"], confidence=3),
                EvalEntry(includes=["statement", "financialcondition"], excludes=["detail"], confidence=3),
                EvalEntry(includes=["statement", "condition"], excludes=["detail"], confidence=3),
                EvalEntry(includes=["statement", "assets", "liabilities"], excludes=["detail"], confidence=3),
                EvalEntry(includes=["role/balancesheet"], excludes=["detail"], confidence=3),
                EvalEntry(
                    # special case for "arma.com": ex. 0001625285-21-000004, 0001625285-21-000002,  0001625285-21-000006
                    includes=["role/idr_balancesheet"],
                    excludes=["detail"],
                    confidence=3,
                ),
                EvalEntry(  # special case for "kingsway" only report with details in main BS 0001072627-21-000022
                    includes=["kingsway-financial", "consolidated", "balancesheet"], excludes=[], confidence=3
                ),
                EvalEntry(  # special case for xfleet BS with role cashflow 0001213900-21-019311
                    includes=["www.xlfleet.com", "consolidatedcashflow"], excludes=["cashflow0"], confidence=3
                ),
            ],
            root_keys=[
                EvalEntry(includes=["statementoffinancialposition"], excludes=[], confidence=2),
                EvalEntry(includes=["balancesheet", "parenthetical"], excludes=[], confidence=2),
            ],
            label_list=[],
        ),
        "EQ": StmtEvalDefinition(
            role_keys=[
                EvalEntry(includes=["statement", "shareholder", "equity"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "stockholder", "equity"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "shareowner", "equity"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "stockowner", "equity"], excludes=[], confidence=3),
                EvalEntry(includes=["consolidated", "statement", "equity"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "members", "equity"], excludes=[], confidence=3),
                EvalEntry(includes=["consolidated", "statement", "partner", "capital"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "changes", "partner", "capital"], excludes=[], confidence=3),
                EvalEntry(includes=["shareholder", "equity", "type"], excludes=[], confidence=3),
                EvalEntry(includes=["consolidated", "statement", "changes", "capital"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "changes", "members", "capital"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "changes", "trust", "capital"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "stockholder", "deficit"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "changes", "stockholder", "deficit"], excludes=[], confidence=3),
                EvalEntry(includes=["consolidated", "statement", "shareholder", "deficit"], excludes=[], confidence=3),
                EvalEntry(includes=["consolidated", "statement", "shareowner", "deficit"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "changes", "shareholder", "deficit"], excludes=[], confidence=3),
                EvalEntry(includes=["consolidated", "statement", "capital", "stock"], excludes=[], confidence=3),
                EvalEntry(includes=["consolidated", "statement", "capitalization"], excludes=[], confidence=3),
            ],
            root_keys=[
                EvalEntry(includes=["statement", "shareholder", "equity"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "stockholder", "equity"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "shareowner", "equity"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "stockowner", "equity"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "partner", "capital"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "members", "equity"], excludes=[], confidence=3),
            ],
            label_list=[],
        ),
        "IS": StmtEvalDefinition(
            role_keys=[
                EvalEntry(
                    includes=["consolidated", "statement", "income"], excludes=["comprehensive", "detail"], confidence=3
                ),
                EvalEntry(
                    includes=["consolidated", "statement", "loss"], excludes=["comprehensive", "detail"], confidence=3
                ),
                EvalEntry(
                    includes=["consolidated", "statement", "revenue"],
                    excludes=["comprehensive", "detail"],
                    confidence=3,
                ),
                EvalEntry(
                    includes=["consolidated", "statement", "earnings"],
                    excludes=["comprehensive", "detail"],
                    confidence=3,
                ),
                EvalEntry(
                    includes=["condensed", "statement", "earnings"], excludes=["comprehensive", "detail"], confidence=3
                ),
                EvalEntry(
                    includes=["consolidated", "statement", "operation"],
                    excludes=["comprehensive", "detail"],
                    confidence=3,
                ),
                EvalEntry(
                    includes=["consolidated", "results", "operation"],
                    excludes=["comprehensive", "detail"],
                    confidence=3,
                ),
                EvalEntry(
                    includes=["condensed", "statement", "operation"], excludes=["comprehensive", "detail"], confidence=3
                ),
                EvalEntry(
                    includes=["statement", "operation"],
                    excludes=["comprehensive", "detail", "presentation"],
                    confidence=3,
                ),
                EvalEntry(includes=["statement", "income"], excludes=["comprehensive", "detail"], confidence=3),
                EvalEntry(includes=["statement", "loss"], excludes=["comprehensive", "detail"], confidence=3),
                EvalEntry(includes=["statement", "earnings"], excludes=["comprehensive", "detail"], confidence=3),
                EvalEntry(  # case 00000007789-21-000018 -> IS parenth contains detail in name
                    includes=["consolidated", "statement", "income", "parenthetical"],
                    excludes=["comprehensive"],
                    confidence=3,
                ),
                EvalEntry(  # case 0001213900-21-xxxxxx -> IS is balancesheet0
                    includes=["consolidated", "statement", "income", "parenthetical"],
                    excludes=["comprehensive"],
                    confidence=3,
                ),
                EvalEntry(  # case 0001213900-21-xxxxxx -> IS is balancesheet0
                    includes=["consolidatedbalancesheet_parentheticals0"], excludes=["comprehensive"], confidence=6
                ),
                EvalEntry(  # case 0001213900-21-xxxxxx -> IS is balancesheet0
                    includes=["consolidatedbalancesheet0"], excludes=["comprehensive"], confidence=6
                ),
            ],
            root_keys=[
                EvalEntry(includes=["income", "statement", "abstract"], excludes=["comprehensive"], confidence=2),
            ],
            label_list=[EvalEntry(includes=["operating", "income", "loss"], excludes=["asset"], confidence=1)],
        ),
        "CI": StmtEvalDefinition(
            role_keys=[
                EvalEntry(
                    includes=["comprehensive", "consolidated", "statement", "operation", "loss"],
                    excludes=["detail"],
                    confidence=6,
                ),
                EvalEntry(
                    includes=["comprehensive", "consolidated", "statement", "income"], excludes=["detail"], confidence=3
                ),
                EvalEntry(
                    includes=["comprehensive", "consolidated", "statement", "earnings"],
                    excludes=["detail"],
                    confidence=3,
                ),
                EvalEntry(
                    includes=["comprehensive", "condensed", "statement", "earnings"], excludes=["detail"], confidence=3
                ),
                EvalEntry(
                    includes=["comprehensive", "consolidated", "statement", "loss"], excludes=["detail"], confidence=3
                ),
                EvalEntry(
                    includes=["comprehensive", "consolidated", "statement", "operation"],
                    excludes=["detail"],
                    confidence=3,
                ),
                EvalEntry(
                    includes=["comprehensive", "consolidated", "results", "operation"],
                    excludes=["detail"],
                    confidence=3,
                ),
                EvalEntry(
                    includes=["comprehensive", "consolidated", "statement", "loss"], excludes=["detail"], confidence=3
                ),
                EvalEntry(includes=["comprehensive", "statement", "income"], excludes=["detail"], confidence=3),
                EvalEntry(includes=["comprehensive", "statement", "loss"], excludes=["detail"], confidence=3),
                EvalEntry(includes=["comprehensive", "statement", "operation"], excludes=["detail"], confidence=3),
                EvalEntry(includes=["comprehensive", "consolidated", "income"], excludes=["detail"], confidence=3),
            ],
            root_keys=[
                EvalEntry(includes=["comprehensive", "income", "statement", "abstract"], excludes=[], confidence=2),
                EvalEntry(includes=["income", "statement", "abstract"], excludes=[], confidence=1),
            ],
            label_list=[EvalEntry(includes=["comprehensive"], excludes=["asset"], confidence=1)],
        ),
        "CF": StmtEvalDefinition(
            role_keys=[
                EvalEntry(includes=["consolidated", "statement", "cash", "flow"], excludes=[], confidence=3),
                EvalEntry(  # spelling error 0001052918-21-000009
                    includes=["consoldiated", "statement", "cash", "flow"], excludes=[], confidence=3
                ),
                EvalEntry(includes=["condensed", "statement", "cash", "flow"], excludes=[], confidence=3),
                EvalEntry(includes=["consolidated", "cash", "flow"], excludes=[], confidence=3),
                EvalEntry(includes=["condensed", "cash", "flow"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "cash", "flow"], excludes=[], confidence=3),
                EvalEntry(includes=["statement", "cash", "receipt", "disbursement"], excludes=[], confidence=3),
            ],
            # SonderFall für diesen hier kann man nicht so einfach excluden...
            # ginge nur über labels oder mit regex prüfung
            # { # special case for xfleet BS with role cashflow 0001213900-21-019311
            #     includes= ['www.xlfleet.com', 'consolidatedcashflow'],
            #     excludes= ['cashflow0'],
            #     confidence= 2
            # },
            root_keys=[
                EvalEntry(includes=["statement", "cashflow"], excludes=[], confidence=3),
            ],
            label_list=[
                EvalEntry(includes=["netcashprovided", "operatingactivities"], excludes=[], confidence=6),
            ],
        ),
    }

    def __init__(self):
        pass

    def _eval_statement_canditate_helper(self, key: str, definition: List[EvalEntry]) -> int:
        if key is None:
            return 0

        key = key.lower()
        max_confidence = 0
        for key_def in definition:
            includes = key_def.includes
            excludes = key_def.excludes
            confidence = key_def.confidence

            if all(map_key in key for map_key in includes) and not any(map_key in key for map_key in excludes):
                max_confidence = max(max_confidence, confidence)

        return max_confidence

    def _eval_statement_canditate_label_helper(
        self, loc_list: List[SecPreTransformLocationDetails], definition: List[EvalEntry]
    ):
        tag_list_lower = [loc_entry.tag.lower() for loc_entry in loc_list]

        max_confidence = 0
        for key_def in definition:
            includes = key_def.includes
            excludes = key_def.excludes
            confidence = key_def.confidence

            contains_include = False
            contains_exlcude = False
            for tag in tag_list_lower:
                if all(map_key in tag for map_key in includes):
                    contains_include = True
                if any(map_key in tag for map_key in excludes):
                    contains_exlcude = True
            # the included condition has to be present and the excluded conditions may not be present
            if contains_include and not contains_exlcude:
                max_confidence = max(max_confidence, confidence)

        return max_confidence

    def evaluate_statement_canditates(
        self, role: str, root_node: str, loc_list: List[SecPreTransformLocationDetails]
    ) -> Dict[str, StmtConfidence]:
        # returns for matches stmt: {byrole: confidence, byroot:confidence, bylabel: confidence}

        result: Dict[str, StmtConfidence] = {}

        for key, definitions in self.stmt_eval_dict.items():
            role_keys_definition = definitions.role_keys
            root_keys_definition = definitions.root_keys
            label_definition = definitions.label_list

            details = StmtConfidence(
                byRole=self._eval_statement_canditate_helper(role, role_keys_definition),
                byRoot=self._eval_statement_canditate_helper(root_node, root_keys_definition),
                byLabel=self._eval_statement_canditate_label_helper(loc_list, label_definition),
            )

            if details.get_max_confidenc() > 0:
                result[key] = details

        return result
