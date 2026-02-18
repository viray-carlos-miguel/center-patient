#!/usr/bin/env python3
"""
Comprehensive System Capability Test - Full System Evaluation
Tests all 120 cases across 5 test suites to demonstrate complete system capability
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

import asyncio
import time
from guaranteed_accuracy_solution import GuaranteedAccuracySystem

class ComprehensiveSystemTest:
    """Comprehensive test of the entire medical AI system capability"""
    
    def __init__(self):
        self.system = GuaranteedAccuracySystem()
        self.start_time = time.time()
        
        # All test suites
        self.test_suites = {
            'Core Medical Conditions': {
                'file': 'final_comprehensive_web_test.py',
                'description': 'Essential medical conditions - fundamental system capability',
                'cases': 10
            },
            'Extended Medical Coverage': {
                'file': 'extended_comprehensive_test.py',
                'description': 'Expanded medical conditions - broader coverage',
                'cases': 15
            },
            'Ultra Comprehensive Edge Cases': {
                'file': 'ultra_comprehensive_test.py',
                'description': 'Edge cases and rare conditions - system limits',
                'cases': 26
            },
            'Extreme Stress Scenarios': {
                'file': 'extreme_comprehensive_test.py',
                'description': 'Challenging scenarios - stress testing',
                'cases': 31
            },
            'Final Stress Test': {
                'file': 'final_stress_test.py',
                'description': 'Ultimate stress test - comprehensive validation',
                'cases': 38
            }
        }
    
    async def run_test_suite(self, suite_name: str, suite_info: dict) -> dict:
        """Run a specific test suite"""
        print(f'\n🧪 Running {suite_name}')
        print(f'📋 {suite_info["description"]}')
        print(f'📁 File: {suite_info["file"]}')
        print('=' * 60)
        
        try:
            # Import and run the test suite
            if suite_info['file'] == 'final_comprehensive_web_test.py':
                from final_comprehensive_web_test import ComprehensiveWebTest
                test_runner = ComprehensiveWebTest()
            elif suite_info['file'] == 'extended_comprehensive_test.py':
                from extended_comprehensive_test import ExtendedComprehensiveTest
                test_runner = ExtendedComprehensiveTest()
            elif suite_info['file'] == 'ultra_comprehensive_test.py':
                from ultra_comprehensive_test import UltraComprehensiveTest
                test_runner = UltraComprehensiveTest()
            elif suite_info['file'] == 'extreme_comprehensive_test.py':
                from extreme_comprehensive_test import ExtremeComprehensiveTest
                test_runner = ExtremeComprehensiveTest()
            elif suite_info['file'] == 'final_stress_test.py':
                from final_stress_test import FinalStressTest
                test_runner = FinalStressTest()
            
            # Run the test
            results = await test_runner.run_comprehensive_test()
            
            return {
                'suite_name': suite_name,
                'total_cases': results.get('total_cases', 0),
                'successful_cases': results.get('successful_cases', 0),
                'condition_accuracy': results.get('condition_accuracy', 0),
                'confidence_accuracy': results.get('confidence_accuracy', 0),
                'web_alignment_score': results.get('web_alignment_score', 0),
                'method_breakdown': results.get('method_breakdown', {}),
                'grade': results.get('grade', 'Unknown'),
                'status': 'completed'
            }
            
        except Exception as e:
            print(f'❌ Error running {suite_name}: {str(e)}')
            return {
                'suite_name': suite_name,
                'total_cases': suite_info['cases'],
                'successful_cases': 0,
                'condition_accuracy': 0,
                'confidence_accuracy': 0,
                'web_alignment_score': 0,
                'method_breakdown': {},
                'grade': 'F',
                'status': 'error',
                'error': str(e)
            }
    
    async def run_all_tests(self) -> dict:
        """Run all test suites and compile comprehensive results"""
        print('🚀 COMPREHENSIVE SYSTEM CAPABILITY TEST')
        print('=' * 80)
        print('Testing complete medical AI system capability across all scenarios')
        print(f'Total Test Suites: {len(self.test_suites)}')
        print(f'Total Test Cases: {sum(suite["cases"] for suite in self.test_suites.values())}')
        print('=' * 80)
        
        all_results = []
        total_cases = 0
        total_successful = 0
        total_condition_accuracy = 0
        total_confidence_accuracy = 0
        total_web_alignment = 0
        
        # Run each test suite
        for suite_name, suite_info in self.test_suites.items():
            result = await self.run_test_suite(suite_name, suite_info)
            all_results.append(result)
            
            # Accumulate totals
            total_cases += result['total_cases']
            total_successful += result['successful_cases']
            total_condition_accuracy += result['condition_accuracy'] * result['total_cases']
            total_confidence_accuracy += result['confidence_accuracy'] * result['total_cases']
            total_web_alignment += result['web_alignment_score'] * result['total_cases']
        
        # Calculate overall averages
        overall_success_rate = total_successful / total_cases if total_cases > 0 else 0
        overall_condition_accuracy = total_condition_accuracy / total_cases if total_cases > 0 else 0
        overall_confidence_accuracy = total_confidence_accuracy / total_cases if total_cases > 0 else 0
        overall_web_alignment = total_web_alignment / total_cases if total_cases > 0 else 0
        
        # Calculate overall grade
        if overall_success_rate >= 0.9:
            overall_grade = 'A+ OUTSTANDING'
        elif overall_success_rate >= 0.8:
            overall_grade = 'A EXCELLENT'
        elif overall_success_rate >= 0.7:
            overall_grade = 'B+ VERY GOOD'
        elif overall_success_rate >= 0.6:
            overall_grade = 'B GOOD'
        elif overall_success_rate >= 0.5:
            overall_grade = 'C+ ACCEPTABLE'
        elif overall_success_rate >= 0.4:
            overall_grade = 'C NEEDS IMPROVEMENT'
        else:
            overall_grade = 'D POOR'
        
        # Compile method breakdown
        total_rule_based = sum(result.get('method_breakdown', {}).get('rule_based', 0) for result in all_results)
        total_ml_fallback = sum(result.get('method_breakdown', {}).get('ml_fallback', 0) for result in all_results)
        total_safe_fallback = sum(result.get('method_breakdown', {}).get('safe_fallback', 0) for result in all_results)
        
        end_time = time.time()
        execution_time = end_time - self.start_time
        
        # Display comprehensive results
        print(f'\n🏆 COMPREHENSIVE SYSTEM CAPABILITY RESULTS')
        print('=' * 80)
        print(f'Execution Time: {execution_time:.2f} seconds')
        print(f'Total Test Suites: {len(self.test_suites)}')
        print(f'Total Test Cases: {total_cases}')
        print()
        
        # Individual suite results
        print('📊 INDIVIDUAL SUITE RESULTS:')
        for result in all_results:
            status_icon = '✅' if result['status'] == 'completed' else '❌'
            print(f'   {status_icon} {result["suite_name"]}: {result["successful_cases"]}/{result["total_cases"]} '
                  f'({result["successful_cases"]/result["total_cases"]:.1%}) - Grade: {result["grade"]}')
        
        print(f'\n📈 OVERALL SYSTEM PERFORMANCE:')
        print(f'   Total Cases: {total_cases}')
        print(f'   Successful Cases: {total_successful} ({overall_success_rate:.1%})')
        print(f'   Condition Accuracy: {overall_condition_accuracy:.1%}')
        print(f'   Confidence Accuracy: {overall_confidence_accuracy:.1%}')
        print(f'   Web Alignment Score: {overall_web_alignment:.1%}')
        print(f'   Overall Grade: {overall_grade}')
        
        print(f'\n🔧 METHOD BREAKDOWN:')
        print(f'   Rule Based: {total_rule_based} ({total_rule_based/total_cases:.1%})')
        print(f'   ML Fallback: {total_ml_fallback} ({total_ml_fallback/total_cases:.1%})')
        print(f'   Safe Fallback: {total_safe_fallback} ({total_safe_fallback/total_cases:.1%})')
        
        # System capability assessment
        print(f'\n🎯 SYSTEM CAPABILITY ASSESSMENT:')
        if overall_success_rate >= 0.8:
            print('   🏆 EXCELLENT: System demonstrates outstanding medical AI capability')
            print('   ✅ Ready for production deployment with high reliability')
        elif overall_success_rate >= 0.7:
            print('   🎉 VERY GOOD: System demonstrates strong medical AI capability')
            print('   ✅ Suitable for production with monitoring')
        elif overall_success_rate >= 0.6:
            print('   ✅ GOOD: System demonstrates solid medical AI capability')
            print('   ⚠️  Suitable for production with supervision')
        elif overall_success_rate >= 0.5:
            print('   ⚠️  ACCEPTABLE: System demonstrates basic medical AI capability')
            print('   ❌ Requires improvement before production')
        else:
            print('   ❌ NEEDS WORK: System requires significant improvement')
        
        return {
            'total_suites': len(self.test_suites),
            'total_cases': total_cases,
            'successful_cases': total_successful,
            'overall_success_rate': overall_success_rate,
            'condition_accuracy': overall_condition_accuracy,
            'confidence_accuracy': overall_confidence_accuracy,
            'web_alignment_score': overall_web_alignment,
            'overall_grade': overall_grade,
            'method_breakdown': {
                'rule_based': total_rule_based,
                'ml_fallback': total_ml_fallback,
                'safe_fallback': total_safe_fallback
            },
            'execution_time': execution_time,
            'individual_results': all_results
        }

async def main():
    """Main comprehensive system test execution"""
    print('🚀 INITIALIZING COMPREHENSIVE SYSTEM CAPABILITY TEST')
    print('=' * 80)
    
    # Create and run comprehensive test
    comprehensive_test = ComprehensiveSystemTest()
    results = await comprehensive_test.run_all_tests()
    
    # Final summary
    print(f'\n🎯 COMPREHENSIVE TEST SUMMARY:')
    print(f'   System Grade: {results["overall_grade"]}')
    print(f'   Success Rate: {results["overall_success_rate"]:.1%}')
    print(f'   Total Cases: {results["total_cases"]}')
    print(f'   Execution Time: {results["execution_time"]:.2f}s')
    
    if results["overall_success_rate"] >= 0.7:
        print('\n🏆 YOUR MEDICAL AI SYSTEM DEMONSTRATES EXCELLENT CAPABILITY!')
    elif results["overall_success_rate"] >= 0.6:
        print('\n✅ YOUR MEDICAL AI SYSTEM DEMONSTRATES GOOD CAPABILITY!')
    else:
        print('\n⚠️  YOUR MEDICAL AI SYSTEM NEEDS FURTHER IMPROVEMENT')
    
    return results

if __name__ == "__main__":
    result = asyncio.run(main())
