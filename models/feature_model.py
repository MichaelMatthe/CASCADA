from sympy import Symbol, Implies, And, Or, Not
from sympy.logic.boolalg import truth_table

import json
import os
import pandas

from pathlib import Path

# feature type
BOOL = "bool"
INT = "int"
REAL = "real"

OPTIONAL = "optional"
MANDATORY = "mandatory"

NO_GROUP = "no_group"
OR = "or"
ALTERNATIVE = "alternative"

REQUIRES = "requires"
EXCLUDES = "excludes"

ROOT = "root"
SYSTEM = "system"
CONTEXT = "context"
STRUCTURE = "structure"
CROSS_TREE_CONSTRAINTS = "cross tree constraints"
INTERVAL_SIZE = "interval size"


class Feature:
    """
    Class used to represent a Feature
    """

    def __init__(
        self,
        feature: list[str, str, float, float, str],
        branch: str,
        interval_size: int = 1,
    ) -> None:
        """
        feature: list
            a list of feature attributes [name, type, lb, ub, optional]
        interval_size: float
            the size of intervals for discretization of numerical features (INT, REAL)
        branch: str
            SYSTEM, CONTEXT, None
        """
        self.name = feature[0]
        self.type = feature[1]
        self.lb = feature[2]
        self.ub = feature[3]
        if feature[4] == OPTIONAL:
            self.optional = True
        elif feature[4] == MANDATORY:
            self.optional = False
        else:
            raise ValueError("Invalid optional / mandatory definition", feature)
        self.interval_size = interval_size
        self.branch = branch

        self.parent = None
        self.group_flag = False
        self.symbol = Symbol(self.name)


class Structure:
    """
    Class used to represent a Feature Structure (Alternative-, or-, no-group)
    """

    def __init__(self, parent: str, children: list[str], type: str) -> None:
        """
        parent: Feature
            the parent feature
        children: list of Feature
            list of child features
        relationship: str
            NO_GROUP, ALTERNATIVE, OR
        """
        self.parent = parent
        self.children = children
        self.type = type


class CrossTreeConstraint:
    """
    Class used to represent a Cross-Tree Constraint (requires, excludes)
    """

    def __init__(self, feature_1: str, feature_2: str, constraint: str) -> None:
        """
        feature_1: Feature
            first feature of the constraint
        feature_2: Feature
            second feature of the constraint
        constraint: str
            REQUIRES, EXCLUDES
        """
        self.feature_1 = feature_1
        self.feature_2 = feature_2
        self.constraint = constraint


class NumericalSubFeature:

    def __init__(self, name: str, branch: str, lb: float, ub: float) -> None:
        self.name = name
        self.branch = branch
        self.lb = lb
        self.ub = ub


class FM:

    def __init__(self, json_file):

        with open(json_file) as file:
            fm_json = json.load(file)

        self.features = {}
        self.numerical_sub_features = {}
        self.features[ROOT] = Feature([ROOT, BOOL, 1, 1, MANDATORY], None)
        self.features[SYSTEM] = Feature([SYSTEM, BOOL, 1, 1, MANDATORY], None)
        self.features[SYSTEM].parent = self.features[ROOT]
        self.features[CONTEXT] = Feature([CONTEXT, BOOL, 1, 1, MANDATORY], None)
        self.features[CONTEXT].parent = self.features[ROOT]

        for feature in fm_json[SYSTEM]:
            feature_obj = Feature(feature, SYSTEM)
            self.features[feature_obj.name] = feature_obj
        for feature in fm_json[CONTEXT]:
            feature_obj = Feature(feature, CONTEXT)
            self.features[feature_obj.name] = feature_obj
        for _, feature in self.features.items():
            try:
                feature.interval_size = fm_json[INTERVAL_SIZE][feature.name]
            except KeyError:
                pass

        self.structures = []
        for structure in fm_json[STRUCTURE]:
            child_features = []
            group_type = structure[2]
            for child_name in structure[1]:
                child_features.append(self.features[child_name])
                if group_type != NO_GROUP:
                    self.features[child_name].group_flag = True
                self.features[child_name].parent = self.features[structure[0]]
            self.structures.append(
                Structure(self.features[structure[0]], child_features, group_type)
            )

        self.cross_tree_constraints = []
        for constraint in fm_json[CROSS_TREE_CONSTRAINTS]:
            self.cross_tree_constraints.append(
                self.features[constraint[0]],
                self.features[constraint[1]],
                constraint[2],
            )

        self.fm_pl = And(Implies(True, self.features[ROOT].symbol))
        self.create_feature_relationships()

    def add_pl_term(self, term):
        self.fm_pl = And(self.fm_pl, term)

    def create_feature_relationships(self):
        for feature in self.features.values():
            if not feature.group_flag and feature.parent != None:
                # feature is not part of a group
                self.add_pl_term(Implies(feature.symbol, feature.parent.symbol))
                if not feature.optional:
                    # feature is mandatory
                    self.add_pl_term(Implies(feature.parent.symbol, feature.symbol))

        for structure in self.structures:
            if structure.type == OR:
                self.add_pl_term(
                    And(
                        Implies(
                            structure.parent.symbol,
                            Or(*[child.symbol for child in structure.children]),
                        ),
                        Implies(
                            Or(*[child.symbol for child in structure.children]),
                            structure.parent.symbol,
                        ),
                    )
                )
            elif structure.type == ALTERNATIVE:
                for child in structure.children:
                    conjunctive_terms = [structure.parent.symbol]
                    for other_child in structure.children:
                        if child.name != other_child.name:
                            conjunctive_terms.append(Not(other_child.symbol))

                    self.add_pl_term(
                        And(
                            Implies(child.symbol, And(*conjunctive_terms)),
                            Implies(And(*conjunctive_terms), child.symbol),
                        )
                    )
            elif structure.type == NO_GROUP:
                pass
            else:
                raise ValueError(
                    "Invalid structure type", structure.parent.name, structure.type
                )

    def generate_truth_table(self) -> list[list[int]]:
        fm_file_path = "fm_saves/fm_valid_configs.json"
        fm_file = Path(fm_file_path)

        os.makedirs("fm_saves", exist_ok=True)

        if fm_file.is_file():
            with open(fm_file_path, "r") as f:
                valid_table = json.load(f)
        else:
            valid_table = []
            table = truth_table(
                self.fm_pl, [feature.symbol for feature in self.features.values()]
            )
            for line in table:
                if line[-1]:
                    valid_table.append(line[0])
            with open(fm_file_path, "w") as f:
                json.dump(valid_table, f)

        return valid_table


class NumericalFM(FM):

    def __init__(self, json_file: dict) -> None:
        super().__init__(json_file)

        self.system_feature_names = []
        self.context_feature_names = []
        self.valid_configurations_numerical = self.generate_numerical_truth_table()

    def generate_numerical_truth_table(self) -> pandas.DataFrame:
        valid_table = self.generate_truth_table()

        ordered_names = list(self.features.keys())
        system_names = []
        context_names = []
        # Handle numerical features
        for parent_feature_index, feature in enumerate(self.features.values()):
            if feature.type == INT or feature.type == REAL:

                if feature.branch == SYSTEM:
                    system_names.append(feature.name)
                elif feature.branch == CONTEXT:
                    context_names.append(feature.name)

                range_lb = feature.lb
                range_ub = feature.ub
                range_interval_size = feature.interval_size

                if feature.type == REAL:
                    range_ub = int((range_ub - range_lb) / range_interval_size)
                    range_lb = 0
                    range_interval_size = 1
                else:
                    range_ub += 1

                numerical_sub_feature_list = []
                for index_match in range(range_lb, range_ub, range_interval_size):
                    sub_feature_name = feature.name + "_" + str(index_match)
                    ordered_names.append(sub_feature_name)

                    numerical_sub_feature_list.append(
                        NumericalSubFeature(
                            sub_feature_name,
                            feature.branch,
                            feature.lb + feature.interval_size * index_match,
                            feature.lb + (index_match + 1) * feature.interval_size,
                        )
                    )
                    if feature.branch == SYSTEM:
                        system_names.append(sub_feature_name)
                    elif feature.branch == CONTEXT:
                        context_names.append(sub_feature_name)

                self.numerical_sub_features[feature.name] = numerical_sub_feature_list

                temp_valid_table = []
                for entry in valid_table:
                    # check if feature is part of valid config
                    if entry[parent_feature_index] == 1:

                        for index_match in range(
                            range_lb, range_ub, range_interval_size
                        ):
                            temp_valid_table.append(
                                entry
                                + [
                                    1 if index == index_match else 0
                                    for index in range(
                                        range_lb, range_ub, range_interval_size
                                    )
                                ]
                            )
                    else:
                        temp_valid_table.append(
                            entry
                            + [
                                0
                                for _ in range(range_lb, range_ub, range_interval_size)
                            ]
                        )

                    valid_table = temp_valid_table

        self.system_feature_names = sorted(
            system_names, key=lambda x: ordered_names.index(x)
        )
        self.context_feature_names = sorted(
            context_names, key=lambda x: ordered_names.index(x)
        )
        return pandas.DataFrame(valid_table, columns=ordered_names)

    def numerical_feature_name_to_value_range(self, numerical_feature_name):
        for numerical_features in self.numerical_sub_features.values():
            for sub_feature in numerical_features:
                if sub_feature.name == numerical_feature_name:
                    return (sub_feature.lb, sub_feature.ub)
        raise ValueError("Numerical sub feature does not exist", numerical_feature_name)

    def numerical_feature_value_to_numerical_name(self, feature_name, value):
        last_feature = None
        for sub_feature in self.numerical_sub_features[feature_name]:
            last_feature = sub_feature
            if value >= sub_feature.lb and value < sub_feature.ub:
                return sub_feature.name
        if last_feature.ub == value and self.features[feature_name].type == REAL:
            return last_feature.name
        raise ValueError(
            "Value outside of valid range",
            "feature: {}, value: {}".format(feature_name, value),
        )


if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), "..", "swim", "swim_fm.json")
    feature_model = FM(os.path.abspath(file_path))
