import unittest
import csv
import tako
import sys
import copy
sys.path.append('..')
from dgeann import dgeann

class testGenetics(unittest.TestCase):

    def setUp(self):
        tako.random.seed("genetics")
        self.fields = ['dom', 'can_mut', 'can_dup', 'mut_rate', 'ident',
                      'weight', 'in_node', 'out_node', 'in_layer', 'out_layer']

    #'plain' diploid
    def test_p_diploid(self):
        tak = tako.Tako.default_tako(0, True, 0, 0, "Plain", False)
        for i in range(len(tak.genome.layerchr_a)):
            self.assertEqual(tak.genome.weightchr_a[i].ident,
                             tak.genome.weightchr_b[i].ident)
            self.assertEqual(tak.genome.weightchr_a[i].in_node,
                             tak.genome.weightchr_b[i].in_node)
            self.assertEqual(tak.genome.weightchr_a[i].out_node,
                             tak.genome.weightchr_b[i].out_node)
            self.assertEqual(tak.genome.weightchr_a[i].weight,
                             tak.genome.weightchr_b[i].weight)
            self.assertEqual(tak.genome.weightchr_a[i].mut_rate,
                             tak.genome.weightchr_b[i].mut_rate)

    #'diverse' diploid
    def test_d_diploid(self):
        tak = tako.Tako.default_tako(0, True, 0, 0, "Diverse", False)
        for i in range(len(tak.genome.layerchr_a)):
            self.assertNotEqual(tak.genome.weightchr_a[i].ident,
                             tak.genome.weightchr_b[i].ident)
            self.assertEqual(tak.genome.weightchr_a[i].in_node,
                             tak.genome.weightchr_b[i].in_node)
            self.assertEqual(tak.genome.weightchr_a[i].out_node,
                             tak.genome.weightchr_b[i].out_node)
            self.assertNotEqual(tak.genome.weightchr_a[i].weight,
                             tak.genome.weightchr_b[i].weight)

    def test_haploid(self):
        tak = tako.Tako.default_tako(0, True, 0, 0, "Haploid", False)
        with open("Default Genetics/15_a.csv") as file:
            r = csv.DictReader(file, fieldnames=self.fields)
            i = 0
            for row in r:
                self.assertEqual(tak.genome.weightchr_a[i].ident,
                                 row['ident'])
                self.assertEqual(tak.genome.weightchr_a[i].in_node,
                                 int(row['in_node']))
                self.assertEqual(tak.genome.weightchr_a[i].mut_rate,
                                 float(row['mut_rate']))
                self.assertEqual(tak.genome.weightchr_a[i].weight,
                                 float(row['weight']))
                i += 1

    def test_randnet(self):
        tak = tako.Tako.default_tako(0, True, 0, 0, "Haploid", True)
        for i in range(len(tak.genome.weightchr_a)):
            self.assertEqual(tak.genome.weightchr_a[i].weight,
                             tak.genome.weightchr_b[i].weight)

    def test_mating(self):
        tak_1 = tako.Tako.default_tako(0, True, 0, 0, "Plain", False)
        tak_2 = tako.Tako.default_tako(0, True, 0, 1, "Plain", False)
        result = tak_1.mated(tak_2)
        self.assertEqual(result, ("amuse", -1))
        tak_1.desire = 150
        result = tak_1.mated(tak_2)
        self.assertEqual(result, ("amuse", -1))
        tak_1.desire = 0
        tak_2.desire = 150
        tak_2.dez = 250
        result = tak_1.mated(tak_2)
        self.assertEqual(result, ("amuse", -1))
        tak_1.desire = 100
        tak_1.dez = 150
        result = tak_1.mated(tak_2)
        self.assertEqual(len(result), 6)
        self.assertEqual(tak_1.desire, 0)
        self.assertEqual(tak_2.desire, 0)
        self.assertEqual(tak_1.dez, 0)
        self.assertEqual(tak_2.dez, 0)
        tak_1.update()
        tak_2.update()
        self.assertAlmostEqual(tak_1.desire, 0.01, places=2)
        self.assertAlmostEqual(tak_2.desire, 0.01, places=2)
        self.assertEqual(tak_1.dez, 1)
        self.assertEqual(tak_2.dez, 1)

    def test_genoverlap(self):
        tako.family_detection = "Genoverlap"
        tako.family_mod = 1
        tak_1 = tako.Tako.default_tako(0, True, 0, 0, "Diverse", False)
        tak_2 = copy.copy(tak_1)
        self.assertEqual(tak_1.genoverlap(tak_2), 1.0)
        self.assertEqual(tak_1.mated(tak_2), [("amuse", -30)])
        tak_3 = tako.Tako.default_tako(0, True, 0, 0, "Diverse", False)
        self.assertEqual(tak_1.genoverlap(tak_3), 0.0)
        tak_1.desire = 150
        tak_3.desire = 150
        gen_4 = tak_1.mated(tak_3)[3]
        tak_4 = tako.Tako(0, True, 0, 0, gen_4, "tak_4", None,
                          [tak_1.ident, tak_3.ident], 1)
        self.assertEqual(tak_4.genoverlap(tak_1), 0.5)
        self.assertEqual(tak_4.genoverlap(tak_3), 0.5)
        tak_1.desire = 150
        tak_3.desire = 150
        gen_5 = tak_1.mated(tak_3)[3]
        tak_5 = tako.Tako(0, True, 0, 0, gen_5, "tak_5", None,
                          [tak_1.ident, tak_3.ident], 1)
        self.assertAlmostEqual(tak_5.genoverlap(tak_4), 0.71, 2)
        self.assertAlmostEqual(tak_4.genoverlap(tak_5), 0.71, 2)
        tak_4.desire = 150
        tak_5.desire = 150
        tako.random.random()
        gen_6 = tak_5.mated(tak_4)[3]
        tak_6 = tako.Tako(0, True, 0, 0, gen_6, "tak_6", None,
                          [tak_4.ident, tak_5.ident], 1)
        self.assertAlmostEqual(tak_6.genoverlap(tak_4), 0.83, 2)

    def test_degree_setting(self):
        tako.family_detection = "Degree"
        tako.family_mod = 1
        GGP1 = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        GGP2 = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        GP2 = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        GP3 = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        GP4 = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        G5 = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        P3 = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        tako_l = [GGP1, GGP2, GP2, GP3, GP4, G5, P3]
        for tak in tako_l:
            tak.desire = 150
        GA = tako.Tako(0, True, 0, 0, GGP1.mated(GGP2)[3], "GA", None,
                          [GGP1, GGP2], 1)
        GGP1.desire = 150
        GGP2.desire = 150
        GP1 = tako.Tako(0, True, 0, 0, GGP1.mated(GGP2)[3], "GP1", None,
                          [GGP1, GGP2], 1)
        tako_l.append(GP1)
        GP1.desire = 150
        A1 = tako.Tako(0, True, 0, 0, GP1.mated(GP2)[3], "A1", None,
                          [GP1, GP2], 1)
        A2 = tako.Tako(0, True, 0, 0, GP3.mated(GP4)[3], "A2", None,
                          [GP3, GP4], 1)
        tako_l.append(A1)
        tako_l.append(A2)
        A_M1 = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        tako_l.append(A_M1)
        for tak in tako_l:
            tak.desire = 150
        P1 = tako.Tako(0, True, 0, 0, GP1.mated(GP2)[3], "P1", None,
                          [GP1, GP2], 1)
        P2 = tako.Tako(0, True, 0, 0, GP3.mated(GP4)[3], "P2", None,
                          [GP3, GP4], 1)
        GP4.desire = 150
        HA = tako.Tako(0, True, 0, 0, GP4.mated(G5)[3], "HA", None,
                          [GP4, G5], 1)
        CO = tako.Tako(0, True, 0, 0, A_M1.mated(A1)[3], "CO", None,
                          [A_M1, A1], 1)
        tako_l = [P1, P2, A1]
        for tak in tako_l:
            tak.desire = 150
        Sib = tako.Tako(0, True, 0, 0, P1.mated(P2)[3], "Sib", None,
                          [P1, P2], 1)
        P1.desire = 150
        P2.desire = 150
        Center = tako.Tako(0, True, 0, 0, P1.mated(P2)[3], "Center", None,
                          [P1, P2], 1)
        P2.desire = 150
        HS = tako.Tako(0, True, 0, 0, P2.mated(P3)[3], "HS", None,
                          [P2, P3], 1)
        DC = tako.Tako(0, True, 0, 0, A1.mated(A2)[3], "DC", None,
                          [A1, A2], 1)
        Sib_m = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        Center_m = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        HS_m = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        Nib_m = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        C_m = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        GC_m = tako.Tako.default_tako(0, True, 0, 0, "Diverse", True)
        tako_list = [Center, Sib, HS, Sib_m, Center_m, HS_m, Nib_m,
                     C_m, GC_m]
        for tak in tako_list:
            tak.desire = 150
        Nib = tako.Tako(0, True, 0, 0, Sib.mated(Sib_m)[3], "Nib", None,
                          [Sib, Sib_m], 1)
        C = tako.Tako(0, True, 0, 0, Center.mated(Center_m)[3], "C", None,
                          [Center, Center_m], 1)
        HNib = tako.Tako(0, True, 0, 0, HS.mated(HS_m)[3], "HNib", None,
                          [HS, HS_m], 1)
        Nib.desire = 150
        GNib = tako.Tako(0, True, 0, 0, Nib.mated(Nib_m)[3], "GNib", None,
                          [Nib, Nib_m], 1)
        C.desire = 150
        GC = tako.Tako(0, True, 0, 0, C.mated(C_m)[3], "GC", None,
                          [C, C_m], 1)
        GC.desire = 150
        GGC = tako.Tako(0, True, 0, 0, GC.mated(GC_m)[3], "GGC", None,
                          [GC, GC_m], 1)
        self.assertEqual(Center.children, [C])
        self.assertEqual(Center.parents, [P1, P2])
        self.assertEqual(Center.siblings, [Sib])
        self.assertEqual(Center.half_siblings, [HS])
        self.assertEqual(Center.niblings, [Nib])
        self.assertEqual(Center.auncles, [A1, A2])
        self.assertEqual(Center.double_cousins, [DC])
        self.assertEqual(Center.cousins, [CO])
        self.assertEqual(Center.grandchildren, [GC])
        self.assertEqual(Center.grandparents, [GP1, GP2, GP3, GP4])
        self.assertEqual(Center.half_niblings, [HNib])
        self.assertEqual(Center.half_auncles, [HA])
        self.assertEqual(Center.great_grandchildren, [GGC])
        self.assertEqual(Center.great_grandparents, [GGP1, GGP2])
        self.assertEqual(Center.great_niblings, [GNib])
        self.assertEqual(Center.great_auncles, [GA])

        self.assertEqual(C.parents, [Center, Center_m])
        self.assertEqual(P1.children, [Sib, Center])
        self.assertEqual(P2.children, [Sib, Center, HS])
        self.assertEqual(DC.double_cousins, [Sib, Center])
        self.assertEqual(GNib.great_auncles, [Center])
        self.assertEqual(GNib.grandparents, [Sib, Sib_m])
        self.assertEqual(GA.great_niblings, [CO, Sib, Center, DC])
        self.assertEqual(HS.double_cousins, [])

if __name__ == '__main__':
    unittest.main()
    
