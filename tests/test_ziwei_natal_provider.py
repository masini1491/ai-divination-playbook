import unittest

from tools.ziwei_natal_provider import NormalizedNatalInput, calculate_scope_a_natal

class ZiWeiScopeANatalProviderTests(unittest.TestCase):
    def test_ding_mao_fixture_matches_pinned_reference(self):
        chart=calculate_scope_a_natal(NormalizedNatalInput(1987,5,20,"酉","fixture:matharts/ziwei@596f43c"))
        self.assertEqual(chart["year_pillar"],{"stem":"丁","branch":"卯"})
        self.assertEqual(chart["life_palace"]["branch"],"酉")
        self.assertEqual(chart["body_palace"]["branch"],"卯")
        self.assertEqual(chart["five_element_bureau"],{"number":5,"label":"土五局"})
        self.assertEqual(chart["ziwei_branch"],"巳")
        self.assertEqual(chart["major_star_placements"],{
            "紫微":"巳","天機":"辰","太陽":"寅","武曲":"丑","天同":"子","廉貞":"酉",
            "天府":"亥","太陰":"子","貪狼":"丑","巨門":"寅","天相":"卯","天梁":"辰","七殺":"巳","破軍":"酉",
        })
        expected={"寅":"奴僕宮","卯":"遷移宮","辰":"疾厄宮","巳":"財帛宮","午":"子女宮","未":"夫妻宮",
                  "申":"兄弟宮","酉":"命宮","戌":"父母宮","亥":"福德宮","子":"田宅宮","丑":"官祿宮"}
        self.assertEqual({x["branch"]:x["palace"] for x in chart["palaces"]},expected)

    def test_xin_you_fixture_matches_pinned_reference(self):
        chart=calculate_scope_a_natal(NormalizedNatalInput(1981,11,7,"丑","fixture:matharts/ziwei@596f43c"))
        self.assertEqual(chart["year_pillar"],{"stem":"辛","branch":"酉"})
        self.assertEqual(chart["life_palace"]["branch"],"亥")
        self.assertEqual(chart["body_palace"]["branch"],"丑")
        self.assertEqual(chart["five_element_bureau"],{"number":3,"label":"木三局"})
        self.assertEqual(chart["ziwei_branch"],"午")
        self.assertEqual(chart["major_star_placements"]["天府"],"戌")
        self.assertEqual(chart["major_star_placements"]["破軍"],"申")

    def test_topology_and_scope_a_retrieval_tokens_are_complete(self):
        chart=calculate_scope_a_natal(NormalizedNatalInput(1987,5,20,"酉","synthetic"))
        self.assertEqual(len(chart["palaces"]),12)
        self.assertEqual(len(chart["major_star_placements"]),14)
        self.assertEqual(len(chart["retrieval_facts"]),26)
        self.assertEqual(chart["topology"]["命宮"]["opposite_palace"],"遷移宮")
        self.assertEqual(set(chart["topology"]["命宮"]["sanfang_palaces"]),{"財帛宮","官祿宮"})
        self.assertFalse(chart["production_authority_granted"])
        self.assertEqual(chart["unsupported"]["dynamic"],"not_computed")

    def test_normalization_boundary_fails_closed(self):
        with self.assertRaises(ValueError):
            calculate_scope_a_natal(NormalizedNatalInput(1987,13,20,"酉","synthetic"))
        with self.assertRaises(ValueError):
            calculate_scope_a_natal(NormalizedNatalInput(1987,5,20,"X","synthetic"))
        with self.assertRaises(ValueError):
            calculate_scope_a_natal(NormalizedNatalInput(1987,5,20,"酉",""))

if __name__=="__main__":
    unittest.main()
